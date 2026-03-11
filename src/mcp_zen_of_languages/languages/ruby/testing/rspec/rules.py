"""RSpec zen principles as Pydantic models."""

from __future__ import annotations

from mcp_zen_of_languages.rules.base_models import LanguageZenPrinciples
from mcp_zen_of_languages.rules.base_models import PrincipleCategory
from mcp_zen_of_languages.rules.base_models import ZenPrinciple


RSPEC_ZEN = LanguageZenPrinciples(
    language="rspec",
    name="RSpec",
    philosophy="RSpec Zen — readable, isolated, and confident Ruby specifications",
    source_text="RSpec documentation and Ruby testing best practices",
    principles=[
        ZenPrinciple(
            id="rspec-001",
            principle="it blocks must have explicit descriptions",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description=(
                "Anonymous it blocks (without a string description) produce cryptic "
                "output and make it impossible to identify failing examples without "
                "reading the implementation."
            ),
            violations=[
                "it { expect(subject).to be_valid }  # no description",
                "it do ... end  # anonymous block",
            ],
            recommended_alternative='it "is valid with all required attributes" do',
        ),
        ZenPrinciple(
            id="rspec-002",
            principle="Use let not instance variables in examples",
            category=PrincipleCategory.ARCHITECTURE,
            severity=7,
            description=(
                "Instance variables set in before blocks are invisible to readers and "
                "may be nil if the before block is missing. let provides lazy "
                "initialization with clear naming."
            ),
            violations=[
                "@user = create(:user)  # in before block",
            ],
            recommended_alternative="let(:user) { create(:user) }",
        ),
        ZenPrinciple(
            id="rspec-003",
            principle="let! only when eager evaluation required",
            category=PrincipleCategory.CORRECTNESS,
            severity=5,
            description=(
                "let! forces eager evaluation, running before every example even when "
                "not needed. This increases test runtime unnecessarily. Use let for "
                "lazy evaluation unless side effects require eager setup."
            ),
            violations=[
                "let!(:user) { create(:user) }  # runs even when test doesn't use it",
            ],
            recommended_alternative="let(:user) { create(:user) } # lazy",
        ),
        ZenPrinciple(
            id="rspec-004",
            principle="Single it block should have at most one expectation",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description=(
                "Multiple expectations in one example mean a failure in the first "
                "hides failures in subsequent ones. Single-expectation examples "
                "give precise failure diagnosis."
            ),
            violations=[
                "it 'validates user' do\n  expect(user.name).to ...\n  expect(user.email).to ...\nend",
            ],
            recommended_alternative="Split into separate it blocks, one per expectation",
        ),
        ZenPrinciple(
            id="rspec-005",
            principle="subject must be explicit when used in it blocks",
            category=PrincipleCategory.READABILITY,
            severity=6,
            description=(
                "Implicit subject (the described class) used inside an it block "
                "is invisible to readers. Explicit subject declarations make the "
                "intent clear."
            ),
            violations=[
                "subject { described_class.new(params) }  # unclear what's being tested",
            ],
            recommended_alternative="subject(:user) { described_class.new(valid_params) }",
        ),
        ZenPrinciple(
            id="rspec-006",
            principle="before(:all) must not mutate shared state",
            category=PrincipleCategory.ARCHITECTURE,
            severity=9,
            description=(
                "before(:all) runs once before all examples in the group and shares "
                "its database or object mutations across all tests. This creates "
                "inter-test dependencies that cause intermittent failures."
            ),
            violations=[
                "before(:all) { @db.truncate! }  # shared state mutation",
            ],
            recommended_alternative="Use before(:each) or database_cleaner strategy",
        ),
        ZenPrinciple(
            id="rspec-007",
            principle="Avoid allow_any_instance_of",
            category=PrincipleCategory.CORRECTNESS,
            severity=7,
            description=(
                "allow_any_instance_of stubs all instances of a class, making tests "
                "fragile and hiding which specific object is being mocked. "
                "It is deprecated in newer RSpec versions."
            ),
            violations=[
                "allow_any_instance_of(User).to receive(:send_email)",
            ],
            recommended_alternative="Inject a specific instance double and stub that",
        ),
        ZenPrinciple(
            id="rspec-008",
            principle="Pending examples must not grow indefinitely",
            category=PrincipleCategory.ARCHITECTURE,
            severity=5,
            description=(
                "Pending examples that are never implemented provide false coverage "
                "impressions. Review and either implement or delete pending examples "
                "at each sprint boundary."
            ),
            violations=[
                "pending 'implement later'  # never implemented",
                "xit 'should work' do ... end  # skipped indefinitely",
            ],
            recommended_alternative="Implement the example or track it as a tech-debt issue",
        ),
        ZenPrinciple(
            id="rspec-009",
            principle="Use shared_examples for duplicate test logic",
            category=PrincipleCategory.CORRECTNESS,
            severity=6,
            description=(
                "Copy-pasted test logic across multiple contexts is maintenance debt. "
                "shared_examples allow reuse while keeping the specification DRY "
                "and consistent."
            ),
            violations=[
                "Identical it blocks duplicated across multiple describe groups",
            ],
            recommended_alternative="shared_examples_for 'a valid resource' do ... end",
        ),
        ZenPrinciple(
            id="rspec-010",
            principle="Avoid focus markers (fit, fdescribe) in committed code",
            category=PrincipleCategory.CORRECTNESS,
            severity=8,
            description=(
                "Focus markers run only a subset of the suite, causing the CI to pass "
                "with most tests skipped. They must never be committed to the main branch."
            ),
            violations=[
                "fit 'should work' do ... end",
                "fdescribe 'UserService' do ... end",
            ],
            recommended_alternative="Remove focus markers before committing; use tags instead",
        ),
    ],
)
