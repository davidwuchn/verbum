// vsm_tap — pristine tree-of-VSM residual/register tap for llama.cpp.
//
// Attaches to a parent model that llama.cpp serves, via the PUBLIC C API only:
//   - sets llama_context_params.cb_eval to a dumping callback (the readers tier);
//   - filters graph tensors by name regex (verbum registers: ffn_gate, ffn_moe_*,
//     l_out, ...);
//   - dumps full tensor values per (register, layer) to disk + a manifest.
//
// llama.cpp is NOT modified. We link only its exported `llama` + `ggml` targets.
// This is the S2/S3 readers tier of control-plane-path.md, reified on the real host.
//
// The graph names every register as "<name>-<layer>" (ggml_format_name), e.g.
// "ffn_gate-15", so register + layer both come from t->name. The gate tensor has
// ne = {n_ff, n_tokens}; ggml is contiguous in ne[0], so the raw buffer read as
// (n_tokens, n_ff) row-major is exactly the [T, d] matrix opcodes/classify.py wants
// (no transpose). See llama-cpp-vsm-wrapper.md.
//
// License: MIT (verbum). Uses llama.cpp public API (MIT); does not derive its source.

#include "llama.h"
#include "ggml.h"
#include "ggml-backend.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <regex>
#include <fstream>
#include <filesystem>

namespace fs = std::filesystem;

struct tensor_record {
    std::string name;      // e.g. "ffn_gate-15"
    std::string reg;       // e.g. "ffn_gate"
    int         layer;     // e.g. 15  (-1 if none)
    int64_t     ne[4];     // element counts (ne[0] fastest)
    std::string dtype;     // ggml_type_name
    std::string file;      // relative .bin path
    size_t      nbytes;
};

struct cb_state {
    fs::path                 out_dir;
    std::vector<std::regex>  filters;   // anchored ^
    std::vector<tensor_record> records;
    std::vector<uint8_t>     scratch;
    bool                     verbose = false;
};

// Parse the trailing "-<int>" of a graph tensor name into (register, layer).
static void split_name(const std::string & name, std::string & reg, int & layer) {
    size_t dash = name.rfind('-');
    if (dash != std::string::npos && dash + 1 < name.size()) {
        bool all_digit = true;
        for (size_t i = dash + 1; i < name.size(); ++i) {
            if (!isdigit((unsigned char) name[i])) { all_digit = false; break; }
        }
        if (all_digit) {
            reg   = name.substr(0, dash);
            layer = std::atoi(name.c_str() + dash + 1);
            return;
        }
    }
    reg   = name;
    layer = -1;
}

// ggml_backend_sched_eval_callback: fires on every graph node.
// ask=true  -> "are you interested?"  (we say yes to everything, then filter on collect)
// ask=false -> the node has executed; data is available.
static bool tap_cb(struct ggml_tensor * t, bool ask, void * user_data) {
    auto * st = (cb_state *) user_data;
    if (ask) {
        return true; // want the follow-up collect call
    }

    // skip ggml view/reshape artifacts (names like "ffn_moe_weights-0 (reshaped)")
    // — they alias data we already capture under the clean register name.
    if (strchr(t->name, ' ') != nullptr) {
        return true;
    }

    // match name against the register filters (anchored ^, like common debug)
    bool match = st->filters.empty();
    for (const auto & rx : st->filters) {
        if (std::regex_search(t->name, rx)) { match = true; break; }
    }
    if (!match) {
        return true; // not ours; keep the graph running
    }

    // don't try to decode quantized activations (there shouldn't be any among our
    // registers — they are f32/i32); record + skip payload if so.
    const bool quant = ggml_is_quantized(t->type);

    const bool is_host = ggml_backend_buffer_is_host(t->buffer);
    const size_t nbytes = ggml_nbytes(t);
    const uint8_t * data = nullptr;
    if (!quant) {
        if (is_host) {
            data = (const uint8_t *) t->data;
        } else {
            st->scratch.resize(nbytes);
            ggml_backend_tensor_get(t, st->scratch.data(), 0, nbytes);
            data = st->scratch.data();
        }
    }

    tensor_record rec;
    rec.name = t->name;
    split_name(rec.name, rec.reg, rec.layer);
    for (int i = 0; i < 4; ++i) rec.ne[i] = t->ne[i];
    rec.dtype  = ggml_type_name(t->type);
    rec.nbytes = nbytes;
    rec.file   = rec.name + ".bin";

    if (!quant && data) {
        fs::path fp = st->out_dir / rec.file;
        std::ofstream f(fp, std::ios::binary);
        f.write(reinterpret_cast<const char *>(data), (std::streamsize) nbytes);
    }

    if (st->verbose) {
        fprintf(stderr, "tap: %-20s reg=%-14s L=%-3d ne=[%lld,%lld,%lld,%lld] %s %zuB\n",
                rec.name.c_str(), rec.reg.c_str(), rec.layer,
                (long long) rec.ne[0], (long long) rec.ne[1],
                (long long) rec.ne[2], (long long) rec.ne[3],
                rec.dtype.c_str(), rec.nbytes);
    }

    st->records.push_back(std::move(rec));
    return true;
}

static void usage(const char * argv0) {
    fprintf(stderr,
        "usage: %s --model PATH (--prompt TEXT | --prompts-file FILE) --out DIR [options]\n"
        "  --model PATH       gguf model path\n"
        "  --prompt TEXT      single prompt to evaluate (prompt-eval only, no generation)\n"
        "  --prompts-file F   file with one prompt per line; dumps to <out>/<idx>/ each,\n"
        "                     loading the model ONCE (canonical for probe sets)\n"
        "  --out DIR          output directory for dump + manifest.json\n"
        "  --filter REGEX     tensor-name filter (repeatable; anchored ^). default set if none:\n"
        "                     ffn_gate ffn_moe_gate ffn_moe_topk ffn_moe_probs ffn_moe_weights l_out\n"
        "  -ngl N             gpu layers to offload (default 999)\n"
        "  -c N               context size (default 2048)\n"
        "  -v                 verbose per-tensor logging to stderr\n",
        argv0);
}

static std::string json_escape(const std::string & s);

// Process one prompt: tokenize, decode (all-position outputs), dump matched
// tensors + manifest into out_dir. The callback (via st) writes .bin files.
static bool process_prompt(llama_model * model, llama_context * ctx, const llama_vocab * vocab,
                           cb_state & st, const std::string & prompt, const fs::path & out_dir,
                           const std::string & model_path) {
    fs::create_directories(out_dir);
    st.out_dir = out_dir;
    st.records.clear();

    const bool add_bos = llama_vocab_get_add_bos(vocab);
    int n_max = (int) prompt.size() + 8;
    std::vector<llama_token> tokens(n_max);
    int n_tok = llama_tokenize(vocab, prompt.c_str(), (int) prompt.size(),
                               tokens.data(), n_max, add_bos, true);
    if (n_tok < 0) {
        tokens.resize(-n_tok);
        n_tok = llama_tokenize(vocab, prompt.c_str(), (int) prompt.size(),
                               tokens.data(), (int) tokens.size(), add_bos, true);
    }
    tokens.resize(n_tok);
    if (n_tok <= 0) {
        fprintf(stderr, "tokenization produced no tokens for prompt: %s\n", prompt.c_str());
        return false;
    }

    // clear KV/memory so each probe is an independent forward (positions reset).
    llama_memory_clear(llama_get_memory(ctx), true);

    // request OUTPUTS AT EVERY POSITION so the final-layer n_outputs optimization
    // does not prune non-last tokens (faithful to an all-positions forward pass).
    llama_batch batch = llama_batch_init(n_tok, 0, 1);
    batch.n_tokens = n_tok;
    for (int i = 0; i < n_tok; ++i) {
        batch.token[i]     = tokens[i];
        batch.pos[i]       = i;
        batch.n_seq_id[i]  = 1;
        batch.seq_id[i][0] = 0;
        batch.logits[i]    = 1;
    }
    int rc = llama_decode(ctx, batch);
    llama_batch_free(batch);
    if (rc != 0) {
        fprintf(stderr, "llama_decode failed for prompt: %s\n", prompt.c_str());
        return false;
    }

    const int n_embd = llama_model_n_embd(model);
    std::ofstream mf(out_dir / "manifest.json");
    mf << "{\n";
    mf << "  \"model\": \"" << json_escape(model_path) << "\",\n";
    mf << "  \"prompt\": \"" << json_escape(prompt) << "\",\n";
    mf << "  \"n_tokens\": " << n_tok << ",\n";
    mf << "  \"n_embd\": " << n_embd << ",\n";
    mf << "  \"tokens\": [";
    for (int i = 0; i < n_tok; ++i) { mf << tokens[i]; if (i + 1 < n_tok) mf << ", "; }
    mf << "],\n";
    mf << "  \"tensors\": [\n";
    for (size_t i = 0; i < st.records.size(); ++i) {
        const auto & r = st.records[i];
        mf << "    {\"name\": \"" << json_escape(r.name) << "\", "
           << "\"register\": \"" << json_escape(r.reg) << "\", "
           << "\"layer\": " << r.layer << ", "
           << "\"ne\": [" << r.ne[0] << ", " << r.ne[1] << ", " << r.ne[2] << ", " << r.ne[3] << "], "
           << "\"dtype\": \"" << r.dtype << "\", "
           << "\"nbytes\": " << r.nbytes << ", "
           << "\"file\": \"" << json_escape(r.file) << "\"}";
        mf << (i + 1 < st.records.size() ? ",\n" : "\n");
    }
    mf << "  ]\n}\n";
    return true;
}

static std::string json_escape(const std::string & s) {
    std::string o;
    for (char c : s) {
        switch (c) {
            case '"':  o += "\\\""; break;
            case '\\': o += "\\\\"; break;
            case '\n': o += "\\n";  break;
            case '\t': o += "\\t";  break;
            case '\r': o += "\\r";  break;
            default:   o += c;      break;
        }
    }
    return o;
}

int main(int argc, char ** argv) {
    std::string model_path, prompt, out_dir, prompts_file;
    std::vector<std::string> filter_patterns;
    int n_gpu_layers = 999;
    int n_ctx = 2048;
    bool verbose = false;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> std::string {
            if (i + 1 >= argc) { usage(argv[0]); exit(1); }
            return argv[++i];
        };
        if      (a == "--model")  model_path = next();
        else if (a == "--prompt") prompt = next();
        else if (a == "--prompts-file") prompts_file = next();
        else if (a == "--out")    out_dir = next();
        else if (a == "--filter") filter_patterns.push_back(next());
        else if (a == "-ngl")     n_gpu_layers = std::atoi(next().c_str());
        else if (a == "-c")       n_ctx = std::atoi(next().c_str());
        else if (a == "-v")       verbose = true;
        else if (a == "-h" || a == "--help") { usage(argv[0]); return 0; }
        else { fprintf(stderr, "unknown arg: %s\n", a.c_str()); usage(argv[0]); return 1; }
    }
    if (model_path.empty() || out_dir.empty() || (prompt.empty() && prompts_file.empty())) {
        usage(argv[0]);
        return 1;
    }
    if (filter_patterns.empty()) {
        filter_patterns = {"ffn_gate", "ffn_moe_gate", "ffn_moe_topk",
                           "ffn_moe_probs", "ffn_moe_weights", "l_out"};
    }

    // collect prompts: single --prompt -> <out>/ ; --prompts-file -> <out>/<idx>/
    std::vector<std::string> prompts;
    bool per_index = false;
    if (!prompts_file.empty()) {
        std::ifstream pf(prompts_file);
        if (!pf) { fprintf(stderr, "cannot open prompts file: %s\n", prompts_file.c_str()); return 1; }
        std::string line;
        while (std::getline(pf, line)) {
            if (!line.empty() && line.back() == '\r') line.pop_back();
            if (!line.empty()) prompts.push_back(line);
        }
        per_index = true;
    } else {
        prompts.push_back(prompt);
    }
    fs::create_directories(out_dir);

    cb_state st;
    st.verbose = verbose;
    for (const auto & p : filter_patterns) {
        st.filters.emplace_back("^" + p, std::regex::optimize);
    }

    llama_backend_init();

    // --- load model ONCE ---
    llama_model_params mparams = llama_model_default_params();
    mparams.n_gpu_layers = n_gpu_layers;
    llama_model * model = llama_model_load_from_file(model_path.c_str(), mparams);
    if (!model) {
        fprintf(stderr, "failed to load model: %s\n", model_path.c_str());
        return 1;
    }
    const llama_vocab * vocab = llama_model_get_vocab(model);

    // --- context with our eval callback (the readers tap) ---
    llama_context_params cparams = llama_context_default_params();
    cparams.n_ctx = n_ctx;
    cparams.n_batch = n_ctx;
    cparams.cb_eval = tap_cb;
    cparams.cb_eval_user_data = &st;
    llama_context * ctx = llama_init_from_model(model, cparams);
    if (!ctx) {
        fprintf(stderr, "failed to create context\n");
        llama_model_free(model);
        return 1;
    }

    // --- loop over prompts (model loaded once) ---
    int ok = 0;
    for (size_t pi = 0; pi < prompts.size(); ++pi) {
        fs::path pdir = per_index ? (fs::path(out_dir) / std::to_string(pi)) : fs::path(out_dir);
        if (process_prompt(model, ctx, vocab, st, prompts[pi], pdir, model_path)) {
            ok++;
        }
    }
    fprintf(stderr, "vsm_tap: processed %d/%zu prompts -> %s\n",
            ok, prompts.size(), out_dir.c_str());

    llama_free(ctx);
    llama_model_free(model);
    llama_backend_free();
    return 0;
}
