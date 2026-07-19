# Feed Forward

## mementum

Mementum teaches AI to remember with git.
Mementum turns inference into versioned environmental learning.

mementum is a git-backed memory protocol for AI agents.  It uses bash and git to store memories and knowledge in the project's git repo. It uses `mementum/state.md` as working memory, `mementum/memories/` for memories, and `mementum/knowledge/` for long term knowledge documents.  It is deployed as a single compact lambda calculus prompt, and describes the protocol to your AI.

mementum uses git for a few things.

- `git grep` - a knowledge graph
- `git log` - a history graph

mementum is a protocol, not a runtime.  You can create a runtime for it, there is a crude reference implementation in the repo.  The real power comes from re-using what is already in your AI.  It knows how to use git and bash to work with these files.  Mementum just tells it to use these tools in a specific way.

See the prompt in the (https://github.com/michaelwhitford/mementum)[mementum github]

### Open Knowledge Format

#### memories

#### knowledge pages

What deserves to be preserved?
Where does it belong?
Is this transient state or durable knowledge?
Is this an observation, inference, decision, failure, or reusable pattern?
Does this contradict an existing artifact?
What future query or queries should be able to find it?
What is the correct compression level for this knowledge?

All of these force reflection from the model.

Who
What
When
Where
How
Why

state->memory->knowledge

Learning Loop

S = AI state (system prompt, state.md, memories, knowledge)
E = experience from current session
R = reflection/distillation

S+1 = f(S,E,R)

This compounds.

K+1 = K + DeltaK

Every correction, every redaction, every improvement, saved for the next agent.
The project learns by feeding the model's outputs back into the context of it's future computations.

Feed Forward

In the system prompt:

- add memories and knowledge details are learned about the project.
- search past knowledge and memories using `git grep`
- optionally add provenance to git commits, `git log` can be used to search provenance


# history

Every belief or observation can retain provenance, chronology, and authorship through commits and diffs.

# branching

Alternative interpretations can coexist without overwriting another.

# reversibility

Bad or outdated learning can be inspected, reverted, purged.

# composability

humans, agents, scripts, editors, CI, embeddings, unix tools, all can operate on the underlying memory and knowledge artifacts

# auditability

The learned state is inspectable, git ops can track changes back through time.

# interop

Open Knowledge Format standard markdown with yaml frontmatter
You can add a vectordb easily, git hooks can trigger updates

# dependencies

Prompt only directives to an agentic AI
Bash tool
git tool or cli installed

DONE!

Your AI can customize the prompts to fit your runtime exactly.


