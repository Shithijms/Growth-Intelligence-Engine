import py_compile, os, sys

backend_files = [
    "agents/base.py",
    "agents/signal_discovery.py",
    "agents/signal_scorer.py",
    "agents/signal_validator.py",
    "agents/serp_scanner.py",
    "agents/strategy_brief.py",
    "agents/blog_generator.py",
    "agents/blog_critique.py",
    "agents/short_form_generator.py",
    "agents/short_form_critique.py",
    "pipeline/state.py",
    "pipeline/quality_gate.py",
    "pipeline/output_assembler.py",
    "pipeline/graph.py",
    "main.py",
    "config.py",
    "models.py",
]

errors = []
for f in backend_files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"  OK  {f}")
    except py_compile.PyCompileError as e:
        errors.append(f)
        print(f"  ERR {f}: {e}")

if errors:
    print(f"\nFAILED: {len(errors)} files had errors")
    sys.exit(1)
else:
    print(f"\nAll {len(backend_files)} Python files syntax OK")
