from __future__ import annotations

import importlib

import pytest

from mcp_zen_of_languages.analyzers.base import AnalysisContext


def _binding_for(framework: str, rule_id: str):
    mapping_module = importlib.import_module(
        f"mcp_zen_of_languages.frameworks.{framework}.mapping"
    )
    return next(
        binding
        for binding in mapping_module.DETECTOR_MAP.bindings
        if binding.detector_id == rule_id
    )


def _rule_for(framework: str, rule_id: str):
    rules_module = importlib.import_module(
        f"mcp_zen_of_languages.frameworks.{framework}.rules"
    )
    zen = next(
        value
        for name, value in vars(rules_module).items()
        if name.endswith("_ZEN") and getattr(value, "language", None) == framework
    )
    return next(principle for principle in zen.principles if principle.id == rule_id)


def _detect(framework: str, rule_id: str, code: str):
    binding = _binding_for(framework, rule_id)
    rule = _rule_for(framework, rule_id)
    config = binding.config_model(
        principle_id=rule.id,
        severity=rule.severity,
        violation_messages=[rule.principle],
        recommended_alternative=rule.recommended_alternative,
        detectable_patterns=rule.detectable_patterns,
    )
    detector = binding.detector_class()
    context = AnalysisContext(code=code, language=framework)
    return detector.detect(context, config)


@pytest.mark.parametrize(
    ("framework", "rule_id", "code"),
    [
        (
            "react",
            "react-001",
            "items.map((item, index) => <li key={index}>{item.name}</li>)",
        ),
        ("react", "react-002", "<button onClick={() => save()}>Save</button>"),
        (
            "react",
            "react-003",
            "function Widget() { document.querySelector('.card'); return null; }",
        ),
        (
            "react",
            "react-004",
            "function Widget({ ready }) { if (ready) { useEffect(() => {}); } return null; }",
        ),
        (
            "react",
            "react-005",
            "useEffect(() => { window.addEventListener('resize', onResize); }, []);",
        ),
        ("vue", "vue-001", "export default { name: 'Card' }"),
        (
            "vue",
            "vue-002",
            "<script setup>const props = defineProps(['title'])</script>",
        ),
        ("vue", "vue-003", '<li v-for="item in items">{{ item.name }}</li>'),
        (
            "vue",
            "vue-004",
            '<li v-for="item in items" v-if="item.visible">{{ item.name }}</li>',
        ),
        ("vue", "vue-005", "<script setup>props.title = 'updated'</script>"),
        (
            "angular",
            "angular-001",
            "@Component({ selector: 'app-card', template: '' }) export class CardComponent {}",
        ),
        ("angular", "angular-002", "export class CardComponent { data: any; }"),
        (
            "angular",
            "angular-003",
            "this.userService.load().subscribe(user => this.user = user);",
        ),
        (
            "angular",
            "angular-004",
            "@Component({ selector: 'card-item', template: '' }) export class CardItemComponent {}",
        ),
        (
            "angular",
            "angular-005",
            "const routes = [{ path: 'admin', component: AdminComponent }];",
        ),
        (
            "nextjs",
            "nextjs-001",
            'export default function Page() { return <a href="/dashboard">Dashboard</a>; }',
        ),
        (
            "nextjs",
            "nextjs-002",
            'export default function Page() { return <img src="/hero.png" alt="hero" />; }',
        ),
        (
            "nextjs",
            "nextjs-003",
            "export async function getServerSideProps() { return { props: {} }; }",
        ),
        (
            "nextjs",
            "nextjs-004",
            "export async function GET() { return NextResponse.json(error); }",
        ),
        (
            "nextjs",
            "nextjs-005",
            "'use client'; useEffect(() => { fetch('/api/users'); }, []);",
        ),
    ],
)
def test_frontend_framework_detectors_find_rule_violations(
    framework: str,
    rule_id: str,
    code: str,
) -> None:
    violations = _detect(framework, rule_id, code)

    assert violations
    assert violations[0].principle == rule_id


@pytest.mark.parametrize(
    ("framework", "rule_id", "code"),
    [
        (
            "react",
            "react-004",
            "function Widget() { useEffect(() => {}); return null; }",
        ),
        (
            "react",
            "react-005",
            "useEffect(() => { const id = setInterval(tick, 1000); return () => clearInterval(id); }, []);",
        ),
        (
            "vue",
            "vue-003",
            '<li v-for="item in items" :key="item.id">{{ item.name }}</li>',
        ),
        (
            "vue",
            "vue-004",
            '<template v-if="visible"><li v-for="item in items">{{ item.name }}</li></template>',
        ),
        (
            "angular",
            "angular-001",
            "@Component({ selector: 'app-card', changeDetection: ChangeDetectionStrategy.OnPush, template: '' }) export class CardComponent {}",
        ),
        (
            "angular",
            "angular-003",
            "this.userService.load().pipe(takeUntilDestroyed()).subscribe(user => this.user = user);",
        ),
        (
            "nextjs",
            "nextjs-001",
            'export default function Page() { return <Link href="/dashboard">Dashboard</Link>; }',
        ),
        (
            "nextjs",
            "nextjs-005",
            "export default async function Page() { const data = await fetch('https://example.com'); return <div>{data.ok}</div>; }",
        ),
    ],
)
def test_frontend_framework_detectors_avoid_safe_patterns(
    framework: str,
    rule_id: str,
    code: str,
) -> None:
    assert _detect(framework, rule_id, code) == []
