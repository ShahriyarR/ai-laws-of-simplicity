---
name: laws-of-simplicity
description: A standalone skill that guides AI agents to apply John Maeda's 10 Laws of Simplicity throughout the software development lifecycle.
---

# Laws of Simplicity Skill

A standalone skill that guides AI agents to apply John Maeda's 10 Laws of Simplicity throughout the software development lifecycle, ensuring that simplicity principles are considered at every stage from planning to implementation to review.

## Purpose and Scope

This skill provides a framework for AI agents to continuously apply John Maeda's 10 Laws of Simplicity throughout the software development lifecycle. Rather than treating simplicity as an afterthought, agents using this skill will evaluate their work against these principles at every stage - from initial planning and design through implementation, testing, and review.

The skill is designed to be standalone and invocable at any point in the development process, allowing agents to pause and assess whether their current approach aligns with simplicity principles.

## Core Mechanics - The 10 Laws as Actionable Principles

Each of John Maeda's 10 Laws is translated into specific, actionable guidelines that agents can apply during development:

1. **REDUCE**: Continuously question what can be removed or simplified. Before adding features/code, ask "Is this essential?"

2. **ORGANIZE**: Group related functionality to reduce perceived complexity. Use consistent patterns and clear boundaries.

3. **TIME**: Optimize for efficiency - consider how design choices affect development time, build time, and runtime performance.

4. **LEARN**: Prioritize clarity and documentation so others (and future you) can understand the work quickly.

5. **DIFFERENCES**: Balance simplicity with necessary complexity. Know when complexity is needed for functionality.

6. **CONTEXT**: Consider the broader system context - how does this change fit within the entire project?

7. **EMOTION**: Consider the human experience - how does the interface or API feel to use?

8. **TRUST**: Create reliable, predictable systems that users can depend on.

9. **FAILURE**: Accept that some complexity is unavoidable; learn from failures rather than pursuing false simplicity.

10. **THE ONE**: Focus on what truly matters - subtract obvious complexity, add meaningful value.

The skill provides specific checkpoints and questions for each law that agents can invoke at relevant stages.

## Integration with Development Workflow

The skill is designed to work alongside existing skills rather than replace them. Agents can invoke the Laws of Simplicity skill:

- Before starting work: To frame the problem through a simplicity lens
- During brainstorming/design: To evaluate alternative approaches
- Before implementation: To check if the chosen approach aligns with simplicity principles
- During implementation: As a periodic checkpoint to ensure simplicity isn't being lost
- Before code review: To self-evaluate against the laws
- After completion: To reflect on how well the solution embodies simplicity

The skill doesn't dictate HOW to do things (that's left to other skills like brainstorming or debugging), but rather WHAT to consider regarding simplicity at each stage.

## Implementation Approach

This skill is implemented as a standalone skill file that can be loaded by any AI agent supporting skill loading (like OpenCode's skill system). It includes:

1. Clear activation instructions for agents
2. Reference to the 10 Laws with actionable questions
3. Integration points with common development workflows
4. Examples of how to apply each law in practice
5. Guidance on when and how often to invoke the skill

The skill is designed to work with the existing skill infrastructure in agents like OpenCode, requiring no modifications to the agent itself - just dropping the skill file into the appropriate skills directory.

## Activation Instructions

To use this skill, agents should invoke it with the skill tool:
```
skill laws-of-simplicity
```

Upon activation, agents will receive guidance on applying the Laws of Simplicity to their current task.

## Usage Guidelines

Agents should consider invoking this skill:

1. At the beginning of any development task
2. Before making significant architectural decisions
3. When evaluating different implementation approaches
4. Before submitting code for review
5. After completing a task to reflect on simplicity principles applied

## Example Applications

**REDUCE**: When considering adding a new feature, ask "Does this feature provide essential value, or could we achieve the goal with less complexity?"

**ORGANIZE**: When designing a module, group related functions together and separate concerns clearly.

**TIME**: When choosing between algorithms, consider not just Big O notation but also actual implementation time and maintainability.

**LEARN**: When writing code, prioritize clear naming and documentation that reduces the learning curve for others.

**DIFFERENCES**: When simplifying an interface, ensure that necessary functionality isn't sacrificed in the pursuit of false simplicity.

**CONTEXT**: When making changes, consider how they affect other parts of the system and the overall user experience.

**EMOTION**: When designing APIs or interfaces, consider not just functionality but also how they feel to use.

**TRUST**: When implementing error handling, prioritize clarity and predictability over cleverness.

**FAILURE**: When a simplification attempt fails, document what was learned rather than hiding the failure.

**THE ONE**: Regularly step back to ask: "What is the core purpose of this work, and does everything serve that purpose?"

## Checklist for Agents

When working on a task, agents using this skill should periodically ask themselves:

- [ ] Have I considered what could be reduced or removed?
- [ ] Is the organization clear and logical?
- [ ] Have I optimized for time efficiency where it matters?
- [ ] Is this clear enough for others to learn quickly?
- [ ] Have I balanced simplicity with necessary complexity?
- [ ] Does this fit well within the broader context?
- [ ] Have I considered the emotional/user experience?
- [ ] Is this reliable and trustworthy?
- [ ] Have I learned from any failures or false starts?
- [ ] Am I focusing on what truly matters?

---

*Based on "The Laws of Simplicity" by John Maeda*