# The Best AI Agents Will Be the Simplest Ones

*John Maeda's Laws of Simplicity are the missing manual for the agentic era*

---

Everyone is racing to make AI agents do more. More tools. More context. More autonomy. More memory. More plugins. The assumption is obvious: more capability means more value.

It's wrong.

The agents that actually work — the ones that ship code, fix bugs, and don't hallucinate their way into a mess — are the ones that do less, better. They have fewer tools, tighter instructions, and smaller context windows. They are constrained by design, not by accident.

This isn't a new insight. It's the oldest truth in software engineering: simplicity is power. The coder being an LLM doesn't change the physics.

John Maeda codified this decades ago in his 10 Laws of Simplicity. He was writing about design. But he was really writing about systems — and AI agents are systems. His laws are the missing manual for the agentic era.

The best AI agents will be the simplest ones. Here's why.

## Reduce: Give Agents Less, Get More

Maeda's first law is REDUCE. The simplest way to achieve simplicity is through thoughtful reduction. His tenth law completes the thought: simplicity is about subtracting the obvious and adding the meaningful.

This is the entire design philosophy for effective AI agents in one sentence.

Every tool you give an agent is a decision it has to make. Every line of context is something it has to weigh. Every instruction is a constraint it has to reconcile with every other instruction. The agent with 50 tools doesn't have 10x the capability of the agent with 5 — it has 10x the confusion.

The best system prompts aren't the longest ones. They're the ones where every word was fought for, where someone had the discipline to cut the paragraph that "might be useful someday." The best tool sets aren't comprehensive — they're curated.

Simplicity has always required courage. The courage to cut features users asked for. The courage to ship less. In the agentic era, it requires a new kind of courage: the courage to constrain. To give your agent less and trust that less is more.

## Organize: Structure Is the Agent's Immune System

Maeda's second law is ORGANIZE: organization makes a system of many appear fewer. His sixth law adds a critical nuance: what lies in the periphery of simplicity is definitely not peripheral.

For AI agents, this isn't philosophy. It's survival.

The difference between an agent that solves your problem and one that hallucinates a confident-sounding disaster often comes down to one thing: how its context is structured. Not how much context — how it's organized. A well-structured 2,000-token prompt outperforms a chaotic 20,000-token dump every time.

Think about what an agent "sees." It has the instructions you gave it, the tools available to it, the files it can read, the conversation history it carries. That's its world. If that world is cluttered — if tool descriptions overlap, if instructions contradict, if irrelevant files flood the context window — the agent doesn't get confused. It gets creative. And creative agents are dangerous agents.

The periphery matters too. An agent working on a single function still operates within a codebase, a repository, an architecture. The code it can't see shapes the code it writes just as much as the code it can. Good agent design means curating not just what's in focus, but what's in the periphery — making the boundaries clear so the agent knows what it doesn't know.

## Trust: Simplicity Breeds Reliability

Maeda's eighth law is TRUST: in simplicity we trust. His ninth adds the counterweight: some things can never be made simple.

Together, they describe the most important quality an AI agent can have: predictability.

Nobody wants a clever agent. Clever agents surprise you. They "improve" your code in ways you didn't ask for. They refactor when you asked for a fix. They add error handling you didn't need. Cleverness is complexity wearing a mask.

What people actually want is an agent they can rely on. One that does what you asked, the way you'd expect, every time. An agent whose behavior you can predict before you run it. That's trust. And trust is built on simplicity — simple interfaces, simple tool boundaries, simple decision logic.

The ninth law keeps us honest. Not everything can be made simple. Some problems are genuinely complex — distributed systems, legacy migrations, security protocols. Pretending otherwise creates brittle agents that break when reality doesn't match the simplification. The wisdom isn't in making everything simple. It's in knowing which things can be simplified and which must be met on their own terms.

Reliability is simplicity in action. The agent that does one thing well is worth ten that do everything poorly.

## From Philosophy to Practice

These aren't abstract ideas. I've been applying Maeda's laws directly to agentic coding workflows — translating each of the 10 Laws into actionable principles that AI coding agents can follow throughout the development lifecycle. The result is a skill file that agents can load before starting work, giving them a simplicity lens to evaluate every decision from architecture to implementation to code review.

It's open source. You can find it at [REPO_URL] and try it with your own agent setup. The goal isn't to constrain what agents can do — it's to help them focus on what matters.

---

The agentic era is here. The question isn't whether AI agents will write our software — they already are. The question is whether we'll repeat every mistake software engineering has already learned from, or whether we'll carry forward the hard-won wisdom that got us here.

Simplicity has always been the hardest discipline in engineering. It's easy to add. It's easy to build more. The hard part is knowing what to leave out. That was true when humans wrote every line of code, and it's true now that agents write most of it.

The race to build the most capable agent is the wrong race. Capability without simplicity is just sophisticated chaos. The winners in the agentic era won't be the ones who built the most powerful agents. They'll be the ones who built the most focused ones.

Subtract the obvious. Add the meaningful. Everything else is noise.
