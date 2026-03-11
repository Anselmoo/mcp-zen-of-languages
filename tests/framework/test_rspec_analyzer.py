"""Smoke tests for the Ruby RSpec framework analyzer."""

from __future__ import annotations

from mcp_zen_of_languages.languages.ruby.testing.rspec import RSpecAnalyzer


ANALYZER = RSpecAnalyzer()

BAD_CODE_DESCRIPTION = (
    "Triggers: BeforeAllMutationDetector, InstanceVarInBeforeDetector, LetBangDetector, "
    "AnonItDetector, AnyInstanceDetector, PendingExampleDetector, FocusMarkerDetector"
)
BAD_CODE = """\
RSpec.describe MyClass do
  before(:all) do
    @shared_state = MyClass.new
    @shared_state.setup_db!
  end

  let!(:record) { Record.create!(name: "test") }

  it do
    allow_any_instance_of(DatabaseClient).to receive(:query)
    expect(@shared_state.work).to eq(42)
  end

  xit "pending test 1" do; end
  xit "pending test 2" do; end

  fit "focused test — remove before commit" do
    expect(subject.valid?).to be(true)
  end
end
"""

CLEAN_CODE_DESCRIPTION = "A well-formed RSpec file with no violations."
CLEAN_CODE = """\
RSpec.describe MyClass do
  let(:instance) { MyClass.new(valid_params) }

  it "returns 42 when called with valid input" do
    expect(instance.work).to eq(42)
  end

  it "raises ArgumentError for invalid input" do
    expect { instance.invalid_work }.to raise_error(ArgumentError)
  end

  context "when the database is unavailable" do
    let(:db_double) { instance_double(DatabaseClient) }

    before do
      allow(db_double).to receive(:query).and_raise(ConnectionError)
    end

    it "surfaces the error to the caller" do
      expect { instance.work }.to raise_error(ConnectionError)
    end
  end
end
"""

COMMENT_CODE_DESCRIPTION = (
    "Code with comments that contain bad keywords — must NOT produce violations."
)
COMMENTED_BAD_CODE = """\
RSpec.describe MyClass do
  # before(:all) is discouraged — use before(:each) instead.
  # allow_any_instance_of is deprecated in RSpec 3.
  # fit / fdescribe are focus markers that should not be committed.

  let(:subject) { MyClass.new }

  it "works correctly" do
    expect(subject.valid?).to be(true)
  end
end
"""


class TestRSpecAnalyzerFileDetection:
    """is_test_file() correctly identifies RSpec spec files."""

    def test_is_test_file_matches_spec_rb_suffix(self) -> None:
        assert ANALYZER.is_test_file("user_spec.rb") is True

    def test_is_test_file_matches_nested_path(self) -> None:
        assert ANALYZER.is_test_file("spec/models/user_spec.rb") is True

    def test_is_test_file_no_match_plain_rb(self) -> None:
        assert ANALYZER.is_test_file("app/models/user.rb") is False

    def test_is_test_file_no_match_spec_in_dirname(self) -> None:
        # Folder named spec, but filename isn't *_spec.rb.
        assert ANALYZER.is_test_file("spec/support/helpers.rb") is False

    def test_is_test_file_no_match_other_extension(self) -> None:
        assert ANALYZER.is_test_file("user_spec.py") is False


class TestRSpecAnalyzerMetadata:
    """Analyzer metadata is correct."""

    def test_language(self) -> None:
        assert ANALYZER.language() == "rspec"

    def test_parent_language(self) -> None:
        assert ANALYZER.parent_language == "ruby"


class TestRSpecBadCodeViolations:
    """BAD RSpec code produces the expected violations."""

    def test_bad_code_produces_violations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        assert len(result.violations) > 0

    def test_detects_before_all(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("before(:all)" in p or "before" in p.lower() for p in principles)

    def test_detects_instance_var_in_before(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "let" in p.lower() or "instance variable" in p.lower() for p in principles
        )

    def test_detects_let_bang(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("let!" in p or "eager" in p.lower() for p in principles)

    def test_detects_anonymous_it(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "description" in p.lower() or "explicit" in p.lower() for p in principles
        )

    def test_detects_any_instance(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "allow_any_instance_of" in p or "any_instance" in p.lower()
            for p in principles
        )

    def test_detects_pending_example(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("Pending" in p or "pending" in p.lower() for p in principles)

    def test_detects_focus_marker(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "focus" in p.lower() or "fit" in p or "fdescribe" in p for p in principles
        )

    def test_violations_have_locations(self) -> None:
        result = ANALYZER.analyze(BAD_CODE, path="spec/my_class_spec.rb")
        for violation in result.violations:
            assert violation.location is not None
            assert violation.location.line >= 1


class TestRSpecCleanCode:
    """CLEAN RSpec code produces no violations."""

    def test_clean_code_produces_no_violations(self) -> None:
        result = ANALYZER.analyze(CLEAN_CODE, path="spec/my_class_spec.rb")
        assert len(result.violations) == 0

    def test_comment_line_not_flagged(self) -> None:
        """Patterns inside # comments must not trigger detectors."""
        result = ANALYZER.analyze(COMMENTED_BAD_CODE, path="spec/my_class_spec.rb")
        assert len(result.violations) == 0


class TestRSpecIndividualDetectors:
    """Targeted tests for each RSpec detector in isolation."""

    def test_anon_it_do_triggers_violation(self) -> None:
        code = "it do\n  expect(subject).to be_valid\nend\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "description" in p.lower() or "explicit" in p.lower() for p in principles
        )

    def test_anon_it_brace_triggers_violation(self) -> None:
        code = "it { expect(subject).to be_valid }\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "description" in p.lower() or "explicit" in p.lower() for p in principles
        )

    def test_named_it_does_not_trigger_anon_detector(self) -> None:
        code = 'it "works" do\n  expect(1).to eq(1)\nend\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert not any(
            "description" in p.lower() or "explicit" in p.lower() for p in principles
        )

    def test_let_bang_triggers_violation(self) -> None:
        code = "let!(:user) { create(:user) }\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("let!" in p or "eager" in p.lower() for p in principles)

    def test_before_all_triggers_violation(self) -> None:
        code = "before(:all) do\n  @db = DB.new\nend\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("before(:all)" in p for p in principles)

    def test_allow_any_instance_triggers_violation(self) -> None:
        code = "allow_any_instance_of(User).to receive(:send_email)\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("allow_any_instance_of" in p for p in principles)

    def test_expect_any_instance_triggers_violation(self) -> None:
        code = "expect_any_instance_of(User).to receive(:save)\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "allow_any_instance_of" in p or "any_instance" in p.lower()
            for p in principles
        )

    def test_xit_triggers_pending_violation(self) -> None:
        code = 'xit "should work" do; end\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("Pending" in p or "pending" in p.lower() for p in principles)

    def test_xdescribe_triggers_pending_violation(self) -> None:
        code = 'xdescribe "some feature" do; end\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("Pending" in p or "pending" in p.lower() for p in principles)

    def test_pending_keyword_triggers_violation(self) -> None:
        code = 'pending "implement later"\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("Pending" in p or "pending" in p.lower() for p in principles)

    def test_fit_triggers_focus_violation(self) -> None:
        code = 'fit "focused test" do\n  expect(1).to eq(1)\nend\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("focus" in p.lower() or "fit" in p for p in principles)

    def test_fdescribe_triggers_focus_violation(self) -> None:
        code = 'fdescribe "UserService" do; end\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("focus" in p.lower() or "fdescribe" in p for p in principles)

    def test_fcontext_triggers_focus_violation(self) -> None:
        code = 'fcontext "when admin" do; end\n'
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any("focus" in p.lower() for p in principles)

    def test_instance_var_in_before_each(self) -> None:
        """Instance variables inside before(:each) should also be flagged."""
        code = "before do\n  @user = User.new\nend\n"
        result = ANALYZER.analyze(code, path="spec/foo_spec.rb")
        principles = [v.principle for v in result.violations]
        assert any(
            "let" in p.lower() or "instance variable" in p.lower() for p in principles
        )
