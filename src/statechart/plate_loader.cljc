(ns verbum.statechart.plate-loader
  "Delta Plate Loader — VSM as Fulcro Statechart.

  This statechart manages the lifecycle of mmap'd ternary plates:
  crystal (S5), FFN plates (S1), domain plates, and session plates.

  The same statechart definition also compiles to a tensor state machine
  (see scripts/explore/tensor_statechart.py). Both runtimes consume
  the shared definition in specs/plate-loader.edn.

  VSM layers:
    S5 = crystal (identity, mathematical constant, never changes)
    S4 = intelligence (domain shift detection, plate recommendations)
    S3 = plates (control, which plates are loaded/composed)
    S2 = data-model (coordination, guards and thresholds)
    S1 = inference (operations, forward pass on composed plates)

  License: MIT"
  (:require
    [com.fulcrologic.statecharts :as sc]
    [com.fulcrologic.statecharts.chart :refer [statechart]]
    [com.fulcrologic.statecharts.elements :refer
     [assign data-model final on-entry on-exit
      parallel script state transition]]
    [com.fulcrologic.statecharts.events :refer [new-event]]
    [com.fulcrologic.statecharts.protocols :as sp]
    [com.fulcrologic.statecharts.simple :as simple]))

;; ══════════════════════════════════════════════════════════════════════
;; Guards — S2 coordination predicates
;; ══════════════════════════════════════════════════════════════════════

(defn memory-available?
  "Is there memory budget for the requested plate?"
  [env data]
  (let [budget     (get data :memory-budget-mb 4096)
        loaded     (get data :loaded-plates [])
        used       (reduce + 0 (map :size-mb loaded))
        plate-size (get-in (sp/event-data env) [:plate :size-mb] 0)]
    (> (- budget used) plate-size)))

(defn delta-plateau?
  "Has the delta stopped changing? Session 157 fold criterion."
  [_env data]
  (let [frac      (get data :delta-changed-frac 1.0)
        threshold (get data :fold-threshold 0.001)]
    (< frac threshold)))

(defn plates-ready?
  "Is there a composed plate available for inference?"
  [_env data]
  (some? (get data :composed-plate)))

(defn crystal-healthy?
  "Is crystal integrity above the emergency threshold?"
  [_env data]
  (let [loss      (get data :crystal-loss 0.0)
        threshold (get data :algedonic-threshold 0.5)]
    (< loss threshold)))

;; ══════════════════════════════════════════════════════════════════════
;; Actions — S1 operations (mmap, compose, fold)
;; ══════════════════════════════════════════════════════════════════════

(defn load-crystal
  "mmap the crystal file. Read-only. Never unloaded.
  In tensor runtime: np.memmap('crystal.bin', dtype=np.int8, mode='r')"
  [env data]
  (println "  [S5] Loading crystal: crystal.bin (read-only, permanent)")
  ;; In real implementation: mmap the file
  ;; For simulation: record in data model
  {:op :mmap :path "crystal.bin" :mode :readonly})

(defn mmap-plate
  "mmap a plate file from the event payload.
  In tensor runtime: np.memmap(path, dtype=np.int8, mode='r')"
  [env data]
  (let [event-data (sp/event-data env)
        path       (:path event-data)
        plate-id   (:id event-data)]
    (println (str "  [S3] mmap plate: " path " (id: " plate-id ")"))
    {:op :mmap :path path :id plate-id :mode :readonly}))

(defn compose-plates
  "Multiply all loaded plate signs: reduce(sign-multiply, plates).
  In tensor runtime: np.sign(base * domain * session)"
  [env data]
  (let [plates (get data :loaded-plates [])]
    (println (str "  [S3] Composing " (count plates) " plates via sign multiply"))
    {:op :compose :plate-count (count plates)}))

(defn fold-delta
  "Fold delta into base: sign(base × delta) → overwrite base.
  Lossless. Ternary × ternary = ternary."
  [env data]
  (println "  [S3] Folding delta into base plate (irreversible)")
  {:op :fold :method :sign-multiply-inplace})

(defn unload-plate
  "Release mmap'd plate. OS reclaims pages."
  [env data]
  (let [event-data (sp/event-data env)
        plate-id   (:id event-data)]
    (println (str "  [S3] Unloading plate: " plate-id))
    {:op :munmap :id plate-id}))

(defn run-inference
  "Forward pass on composed plates.
  In tensor runtime: the holographic state machine runs on the
  composed plate — Q rotation through crystal basins."
  [env data]
  (println "  [S1] Running inference on composed plates")
  {:op :inference})

(defn diagnose-plates
  "Check crystal loss, plate checksums, NaN detection."
  [env data]
  (println "  [S4] Diagnosing plate integrity")
  {:op :diagnose})

(defn generate-recommendation
  "Analyze inference patterns, suggest plate changes."
  [env data]
  (println "  [S4] Generating plate recommendation")
  {:op :recommend})

;; ══════════════════════════════════════════════════════════════════════
;; The Statechart — VSM as Harel statechart
;; ══════════════════════════════════════════════════════════════════════

(def plate-loader-chart
  "The plate loader VSM expressed as a Fulcro statechart.

  Parallel regions correspond to VSM layers:
    :crystal      = S5 (identity)
    :plates       = S3 (control)
    :inference    = S1 (operations)
    :intelligence = S4 (environment scanning)"
  (statechart {}
    (data-model {:memory-budget-mb    4096
                 :max-plates          8
                 :loaded-plates       []
                 :fold-threshold      0.001
                 :delta-changed-frac  1.0
                 :crystal-loss        0.0
                 :algedonic-threshold 0.5
                 :composed-plate      nil})

    (parallel {:id :system}

      ;; ── S5: Crystal (Identity) ──────────────────────────────────
      ;; Loaded once. Never transitions. The mathematical constant.
      (state {:id :crystal}
        (on-entry {}
          (script {:expr load-crystal})))

      ;; ── S3: Plate Controller (Control) ──────────────────────────
      (state {:id :plates :initial :idle}

        (state {:id :idle}
          (transition {:event :load-plate
                       :target :loading
                       :cond memory-available?}))

        (state {:id :loading}
          (on-entry {}
            (script {:expr mmap-plate}))
          (transition {:event :plate-ready :target :composing})
          (transition {:event :plate-error :target :error}))

        (state {:id :composing}
          (on-entry {}
            (script {:expr compose-plates}))
          (transition {:event :composed :target :ready}))

        (state {:id :ready}
          (transition {:event :infer :target :ready})
          (transition {:event :load-plate
                       :target :loading
                       :cond memory-available?})
          (transition {:event :unload-plate :target :unloading})
          (transition {:event :fold-delta
                       :target :folding
                       :cond delta-plateau?}))

        (state {:id :unloading}
          (on-entry {}
            (script {:expr unload-plate}))
          (transition {:event :unloaded :target :composing})
          (transition {:event :all-unloaded :target :idle}))

        (state {:id :folding}
          (on-entry {}
            (script {:expr fold-delta}))
          (transition {:event :folded :target :ready})
          (transition {:event :fold-error :target :error}))

        (state {:id :error}
          (transition {:event :retry :target :loading})
          (transition {:event :reset :target :idle})))

      ;; ── S1: Inference (Operations) ──────────────────────────────
      (state {:id :inference :initial :waiting}

        (state {:id :waiting}
          (transition {:event :infer
                       :target :running
                       :cond plates-ready?}))

        (state {:id :running}
          (on-entry {}
            (script {:expr run-inference}))
          (transition {:event :inference-complete :target :waiting})
          (transition {:event :inference-error :target :waiting})
          ;; Algedonic alert — bypasses hierarchy (S1 → S5 direct)
          (transition {:event :algedonic :target :halted}))

        (state {:id :halted}
          (transition {:event :reset :target :waiting})
          (transition {:event :diagnose :target :diagnosing}))

        (state {:id :diagnosing}
          (on-entry {}
            (script {:expr diagnose-plates}))
          (transition {:event :diagnosis-ok :target :waiting})
          (transition {:event :plate-corrupt :target :waiting})))

      ;; ── S4: Intelligence (Environment Scanning) ─────────────────
      (state {:id :intelligence :initial :monitoring}

        (state {:id :monitoring}
          (transition {:event :domain-shift-detected :target :recommending})
          (transition {:event :delta-plateau-detected :target :recommending}))

        (state {:id :recommending}
          (on-entry {}
            (script {:expr generate-recommendation}))
          (transition {:event :recommendation-accepted :target :monitoring})
          (transition {:event :recommendation-rejected :target :monitoring}))))))

;; ══════════════════════════════════════════════════════════════════════
;; Simulation — manual event processing
;; ══════════════════════════════════════════════════════════════════════

(comment
  ;; 1. Set up the simple runtime
  (def env (simple/simple-env plate-loader-chart))

  ;; 2. Start the statechart
  (def session-id :plate-session-1)
  (simple/start! env {:session-id session-id})

  ;; 3. Send events — the plate loading lifecycle
  ;;    Each event drives a state transition

  ;; Load a domain plate
  (simple/send! env {:session-id session-id
                     :event (new-event :load-plate
                              {:id :medical
                               :path "plates/medical.delta"
                               :size-mb 567})})

  ;; Plate loaded successfully (internal event from mmap completion)
  (simple/send! env {:session-id session-id
                     :event (new-event :plate-ready)})

  ;; Composition completed
  (simple/send! env {:session-id session-id
                     :event (new-event :composed)})

  ;; Run inference
  (simple/send! env {:session-id session-id
                     :event (new-event :infer {:prompt "What is the diagnosis?"})})

  ;; Inference complete
  (simple/send! env {:session-id session-id
                     :event (new-event :inference-complete)})

  ;; Delta has plateaued — fold it
  ;; (assumes delta-changed-frac has been updated to < threshold)
  (simple/send! env {:session-id session-id
                     :event (new-event :fold-delta)})

  ;; Fold completed
  (simple/send! env {:session-id session-id
                     :event (new-event :folded)})

  ;; Emergency: crystal loss spike (algedonic alert)
  (simple/send! env {:session-id session-id
                     :event (new-event :algedonic {:crystal-loss 0.8})})

  ;; 4. Check state at any point
  (simple/current-configuration env session-id)
  ;; → #{:crystal :ready :waiting :monitoring}
  ;;   (parallel: all four VSM layers active simultaneously)
  )
