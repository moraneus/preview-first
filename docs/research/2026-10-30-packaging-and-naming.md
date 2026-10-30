# Research: skill packaging, popular repos, naming (2026-10-30)

## Spec summary

- Claude Code SKILL.md: https://code.claude.com/docs/en/skills. Frontmatter on line 1. Fields: name (defaults to dir), description, when_to_use, argument-hint, allowed-tools, model, effort, context: fork, paths, metadata, license, compatibility.
- Open Agent Skills spec: https://agentskills.io/specification. name 1-64 chars [a-z0-9-], must equal directory name; description 1-1024; optional license, compatibility, metadata, allowed-tools. Keep to these keys for portability. SKILL.md under 500 lines, references one level deep. Validate: `skills-ref validate ./skill`.
- plugin.json at .claude-plugin/plugin.json: name required (kebab, not claude-/anthropic- prefixed), version, description, author{name,email,url}, homepage, repository, license, keywords, skills. Validate `claude plugin validate --strict .`
- marketplace.json at .claude-plugin/marketplace.json: name, owner.name, plugins[{name, source:"./", description, version, category, tags}]. Install: `/plugin marketplace add owner/repo` then `/plugin install name@marketplace`, or `/plugin install name --marketplace owner/repo`.
- Cross-agent paths (npx skills, https://github.com/vercel-labs/skills/blob/main/docs/agents.md): Claude `.claude/skills/`; Cursor/Codex/OpenCode/Gemini/Copilot/Antigravity `.agents/skills/`; Windsurf `.windsurf/skills/`. `npx skills add owner/repo` discovers root SKILL.md or skills/<name>/SKILL.md. skills.sh badge: https://skills.sh/b/owner/repo.

## Top repos (stars at 2026-10-30)

obra/superpowers 308.8k; affaan-m/ECC 292.8k; anthropics/skills 184.8k; nextlevelbuilder/ui-ux-pro-max-skill 142.6k; thedotmack/claude-mem 105k; ComposioHQ/awesome-claude-skills 78.3k; hesreallyhim/awesome-claude-code 56.9k; wshobson/agents 42k; vercel-labs/skills 37.2k; alirezarezvani/claude-skills 29k; elayadesign/ai-design-skills 12.4k; kaankiziltug/logo-design-skill 5.3k.

## Practices that correlate with stars

1. Two-line Claude Code install at top; repo is its own marketplace (source "./").
2. Universal path via `npx skills add owner/repo`; get indexed on skills.sh.
3. Per-agent install sections listing many harnesses.
4. Hero image or GIF showing output, not chrome.
5. Quantified badges (counts of styles, palettes, devices).
6. Keyword-dense SKILL.md description (drives auto-invocation).
7. "How it works" with an explicit human checkpoint (preview, approve, build).
8. Before/after or examples section with images.
9. Multi-language READMEs.
10. MIT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, semver releases, version bumped in manifests.
11. Tests and evals in repo with CI badge; `claude plugin eval`.
12. Optional thin npm CLI that copies the skill per agent.
13. 10-20 GitHub topics: agent-skills, claude-code, claude-skills, claude-code-plugin, codex, cursor, windsurf, opencode, antigravity, gemini-cli, ui-design, design-system.
14. Landing domain and social proof block.
15. Submit to awesome lists and Anthropic directory (https://claude.ai/directory/manage).

## Naming

Avoid: design-first, style-tiles, designkit, design-canvas, first-look, showme, ui-preview, design-preview, mockup-skill, redesign-skill.
Open: preview-first (chosen), look-before-you-build, previewkit, styleboard, design-peek.
Name repo, plugin.json name, marketplace name, entry name and skills/<name>/ dir identically.
