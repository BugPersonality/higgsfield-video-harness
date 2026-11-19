SHELL := /bin/sh
.DEFAULT_GOAL := help

export PYTHONDONTWRITEBYTECODE := 1

PYTHON ?= python3
SHELL_FILES := $(wildcard scripts/*.sh)

.PHONY: help check test shellcheck docs-check check-instructions \
	intent-check ledger-check campaign-init qa-clip qa-voice qa-render \
	assemble animatic budget-status

help: ## List available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-24s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: check-instructions docs-check shellcheck test ## Run all offline harness checks and unit/integration tests
	@$(PYTHON) scripts/check-intent.py campaigns/example-product-spot
	@$(PYTHON) scripts/check-ledger.py campaigns/example-product-spot

test: ## Run Python unittest suite (validators, mock hf_guard, synthetic FFmpeg QA & assembly)
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

shellcheck: ## Lint all shell scripts with ShellCheck
	@test -n "$(SHELL_FILES)" || exit 0; \
	command -v shellcheck >/dev/null 2>&1 || { echo "shellcheck not installed" >&2; exit 2; }; \
	shellcheck -x -- $(SHELL_FILES)

docs-check: ## Verify all relative Markdown links and heading anchors offline
	$(PYTHON) scripts/check-docs.py .

check-instructions: ## Validate .agents/ roles, skills, openai.yaml, and .codex/config.toml sync
	$(PYTHON) scripts/check-instructions.py .

intent-check: ## Verify campaigns/<CAMPAIGN>/intent.md invariants (CAMPAIGN=<slug|path>)
	@test -n "$(CAMPAIGN)" || { echo "intent-check requires CAMPAIGN=<slug|path>" >&2; exit 2; }
	$(PYTHON) scripts/check-intent.py "$(if $(wildcard $(CAMPAIGN)/intent.md),$(CAMPAIGN),$(if $(wildcard campaigns/$(CAMPAIGN)/intent.md),campaigns/$(CAMPAIGN),$(CAMPAIGN)))"

ledger-check: ## Verify campaigns/<CAMPAIGN>/tasks.md + shotlist.json invariants and print waves
	@test -n "$(CAMPAIGN)" || { echo "ledger-check requires CAMPAIGN=<slug|path>" >&2; exit 2; }
	$(PYTHON) scripts/check-ledger.py "$(if $(wildcard $(CAMPAIGN)/tasks.md),$(CAMPAIGN),$(if $(wildcard campaigns/$(CAMPAIGN)/tasks.md),campaigns/$(CAMPAIGN),$(CAMPAIGN)))"

campaign-init: ## Scaffold a new campaign folder (SLUG=<name> [BRAND=<brand>])
	@test -n "$(SLUG)" || { echo "campaign-init requires SLUG=<name>" >&2; exit 2; }
	$(PYTHON) scripts/campaign_init.py --slug "$(SLUG)" $(if $(BRAND),--brand "$(BRAND)")

budget-status: ## Show spent vs remaining credit envelope for CAMPAIGN=<slug|path>
	@test -n "$(CAMPAIGN)" || { echo "budget-status requires CAMPAIGN=<slug|path>" >&2; exit 2; }
	$(PYTHON) scripts/hf_guard.py status --campaign "$(if $(wildcard $(CAMPAIGN)/intent.md),$(CAMPAIGN),$(if $(wildcard campaigns/$(CAMPAIGN)/intent.md),campaigns/$(CAMPAIGN),$(CAMPAIGN)))"

qa-clip: ## Probe one video clip and optionally write a 3x2 contact sheet (FILE=<mp4> [SHEET=<png>])
	@test -n "$(FILE)" || { echo "qa-clip requires FILE=<path.mp4>" >&2; exit 2; }
	$(PYTHON) scripts/qa_media.py clip "$(FILE)" $(if $(SHEET),--sheet "$(SHEET)")

qa-voice: ## Check VO duration window using 100ms RMS energy (FILE=<wav> WINDOW=<sec>)
	@test -n "$(FILE)" && test -n "$(WINDOW)" || { echo "qa-voice requires FILE=<audio> WINDOW=<sec>" >&2; exit 2; }
	$(PYTHON) scripts/qa_media.py voice "$(FILE)" --window "$(WINDOW)"

qa-render: ## Validate final assembled render loudness, black/frozen frames, and sheet (FILE=<mp4> [SHEET=<png>])
	@test -n "$(FILE)" || { echo "qa-render requires FILE=<path.mp4>" >&2; exit 2; }
	$(PYTHON) scripts/qa_media.py render "$(FILE)" $(if $(SHEET),--sheet "$(SHEET)")

assemble: ## Assemble selected takes from CAMPAIGN=<slug|path> into master.mp4 + stems/
	@test -n "$(CAMPAIGN)" || { echo "assemble requires CAMPAIGN=<slug|path>" >&2; exit 2; }
	@cdir="$(if $(wildcard $(CAMPAIGN)/shotlist.json),$(CAMPAIGN),$(if $(wildcard campaigns/$(CAMPAIGN)/shotlist.json),campaigns/$(CAMPAIGN),$(CAMPAIGN)))"; \
	bash scripts/assemble.sh --campaign "$$cdir" --manifest "$$cdir/shotlist.json" \
		--out "$(or $(OUT),$$cdir/media/exports/master.mp4)" \
		--stems-dir "$(or $(STEMS),$$cdir/media/exports/stems)" \
		$(if $(MUSIC),--music "$(MUSIC)") \
		$(if $(VO),--vo "$(VO)")

animatic: ## Build a zero-video-credit still animatic from approved stills in CAMPAIGN=<slug|path>
	@test -n "$(CAMPAIGN)" || { echo "animatic requires CAMPAIGN=<slug|path>" >&2; exit 2; }
	@cdir="$(if $(wildcard $(CAMPAIGN)/shotlist.json),$(CAMPAIGN),$(if $(wildcard campaigns/$(CAMPAIGN)/shotlist.json),campaigns/$(CAMPAIGN),$(CAMPAIGN)))"; \
	bash scripts/assemble.sh --animatic --campaign "$$cdir" --manifest "$$cdir/shotlist.json" \
		--out "$(or $(OUT),$$cdir/media/exports/animatic.mp4)" \
		$(if $(MUSIC),--music "$(MUSIC)") \
		$(if $(VO),--vo "$(VO)")
