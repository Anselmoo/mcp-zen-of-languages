### Explicit Intent — `ZEN-EXPLICIT-INTENT`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-002` | Quote all variables | 8 |
| Bash | `bash-009` | Use readonly for constants | 6 |
| Bash | `bash-013` | Use arrays instead of string splitting | 7 |
| C++ | `cpp-004` | Prefer nullptr over NULL or 0 | 7 |
| C++ | `cpp-007` | Use const correctness | 8 |
| C++ | `cpp-008` | Avoid C-style casts | 7 |
| C++ | `cpp-012` | Use override and final keywords | 7 |
| C# | `cs-001` | Use nullable reference types | 8 |
| C# | `cs-003` | Prefer var for local variables | 5 |
| C# | `cs-010` | Avoid magic numbers | 6 |
| CSS | `css-002` | Avoid magic pixel values | 6 |
| CSS | `css-003` | Limit inline color literals | 6 |
| CSS | `css-006` | Use a z-index scale | 6 |
| CSS | `css-007` | Avoid manual vendor prefixes | 5 |
| CSS | `css-008` | Use a consistent breakpoint scale | 5 |
| Docker Compose | `docker-compose-002` | Run services as non-root user | 9 |
| Dockerfile | `dockerfile-003` | Prefer COPY over ADD unless extra features are needed | 6 |
| Dockerfile | `dockerfile-008` | Keep .dockerignore coherent with broad context copies | 4 |
| GitHub Actions | `gha-007` | Avoid duplicated step sequences across jobs | 5 |
| GitHub Actions | `gha-010` | Avoid rigid, hardcoded matrix values | 4 |
| GitHub Actions | `gha-013` | Set explicit shell for run steps | 4 |
| GitHub Actions | `gha-015` | Set artifact retention explicitly | 4 |
| GitLab CI | `gitlab-ci-003` | Use allow_failure only with rules-based context | 6 |
| GitLab CI | `gitlab-ci-005` | Reduce duplicated before_script blocks | 5 |
| GitLab CI | `gitlab-ci-010` | Expire artifacts | 5 |
| Go | `go-001` | Errors are values | 9 |
| Go | `go-003` | Make the zero value useful | 6 |
| Go | `go-012` | Avoid init() when possible | 6 |
| Go | `go-017` | Handle every error path | 9 |
| Go | `go-020` | Write self-documenting code | 5 |
| JavaScript | `js-003` | Use strict equality | 8 |
| JavaScript | `js-007` | Handle errors explicitly | 9 |
| JavaScript | `js-008` | Avoid magic numbers and strings | 6 |
| JavaScript | `js-014` | Avoid with statement | 9 |
| JSON | `json-001` | Choose strictness intentionally | 7 |
| JSON | `json-003` | Keys must be unique | 8 |
| JSON | `json-004` | Avoid magic string repetition | 5 |
| JSON | `json-007` | Prefer omission over null sprawl | 5 |
| JSON | `json-008` | Dates must follow ISO 8601 | 6 |
| JSON | `json-009` | Prefer key omission over explicit null | 5 |
| LaTeX | `latex-001` | Prefer \newcommand over \def | 7 |
| LaTeX | `latex-002` | Keep labels and references consistent | 8 |
| LaTeX | `latex-005` | Avoid hardcoded absolute lengths | 5 |
| LaTeX | `latex-006` | Prefer semantic emphasis commands | 4 |
| LaTeX | `latex-008` | Declare UTF-8 encoding intent | 5 |
| Markdown | `md-003` | Avoid bare URLs in prose | 5 |
| Markdown | `md-004` | Fence code blocks with explicit language tags | 4 |
| Markdown | `md-005` | Keep front-matter complete when present | 6 |
| Markdown | `md-006` | Use named default exports in MDX | 6 |
| PowerShell | `ps-005` | Use Write-Verbose and Write-Debug | 6 |
| PowerShell | `ps-012` | Avoid aliases in scripts | 6 |
| PowerShell | `ps-014` | Use script scope carefully | 7 |
| PowerShell | `ps-015` | Handle null values explicitly | 7 |
| Python | `python-002` | Explicit is better than implicit | 7 |
| Python | `python-008` | Special cases aren't special enough to break the rules | 6 |
| Python | `python-009` | Errors should never pass silently | 9 |
| Python | `python-010` | In the face of ambiguity, refuse the temptation to guess | 7 |
| Python | `python-014` | Errors should never pass silently | 8 |
| Rust | `rust-002` | Use the type system to prevent bugs | 8 |
| Rust | `rust-005` | Use #[must_use] for important return types | 6 |
| Rust | `rust-006` | Implement Debug for all public types | 6 |
| Rust | `rust-010` | Prefer enums over booleans for state | 7 |
| Rust | `rust-011` | Use lifetimes judiciously | 6 |
| SQL | `sql-001` | Never use SELECT * | 6 |
| SQL | `sql-002` | Always include INSERT column lists | 7 |
| SQL | `sql-004` | Avoid NOLOCK and dirty reads | 8 |
| SQL | `sql-005` | Avoid implicit type coercion in JOIN predicates | 6 |
| SQL | `sql-007` | Use descriptive table aliases | 4 |
| SQL | `sql-008` | Keep transaction boundaries balanced | 8 |
| SQL | `sql-009` | Prefer explicit JOIN syntax over ANSI-89 comma joins | 6 |
| TOML | `toml-002` | Avoid duplicate keys | 8 |
| TOML | `toml-003` | Use lowercase keys | 5 |
| TOML | `toml-005` | Clarity is paramount | 5 |
| TOML | `toml-007` | Time is specific | 6 |
| TOML | `toml-008` | Floats are not integers | 6 |
| TypeScript | `ts-001` | Avoid 'any' type | 9 |
| TypeScript | `ts-002` | Use strict mode | 9 |
| TypeScript | `ts-004` | Always specify return types | 7 |
| TypeScript | `ts-006` | Leverage type guards | 7 |
| TypeScript | `ts-008` | Avoid non-null assertions | 8 |
| TypeScript | `ts-010` | Prefer unknown over any for uncertain types | 7 |
| TypeScript | `ts-015` | Avoid catch-all types like Object or {} | 6 |
| TypeScript | `ts-016` | Avoid console usage in production code | 4 |
| XML | `xml-001` | Mark up meaning, not presentation | 5 |
| XML | `xml-003` | Namespaces prevent local collisions | 6 |
| XML | `xml-004` | Validity supersedes well-formedness | 6 |
| XML | `xml-006` | Closing tags complete the thought | 5 |
| YAML | `yaml-003` | Avoid duplicate keys | 8 |
| YAML | `yaml-004` | Use lowercase keys | 5 |
| YAML | `yaml-006` | Consistency provides comfort | 5 |
| YAML | `yaml-008` | Strings should look like strings | 6 |

### Flat Traversal — `ZEN-RETURN-EARLY`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-004` | Use $() over backticks | 6 |
| CSS | `css-001` | Avoid specificity creep | 7 |
| GitLab CI | `gitlab-ci-004` | Avoid god pipelines | 6 |
| Go | `go-013` | Organize by responsibility | 6 |
| Go | `go-014` | Embed for composition, not inheritance | 7 |
| Go | `go-016` | Avoid unnecessary complexity | 7 |
| JavaScript | `js-001` | Avoid callback hell | 8 |
| JSON | `json-002` | Keep object depth understandable | 6 |
| JSON | `json-006` | Keep inline arrays bounded | 4 |
| Markdown | `md-001` | Preserve heading hierarchy | 6 |
| Python | `python-003` | Simple is better than complex | 8 |
| Python | `python-005` | Flat is better than nested | 8 |
| Python | `python-015` | Now is better than never | 4 |
| Ruby | `ruby-008` | Use guard clauses | 6 |
| TypeScript | `ts-011` | Use optional chaining instead of manual null checks | 5 |
| TypeScript | `ts-013` | Prefer async/await over raw promise chains | 6 |
| XML | `xml-002` | Attributes for metadata, Elements for data | 5 |
| XML | `xml-005` | Hierarchy represents ownership | 4 |

### Loud Failures — `ZEN-FAIL-FAST`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-001` | Always use set -euo pipefail | 9 |
| Bash | `bash-005` | Check command exit codes | 8 |
| Bash | `bash-010` | Validate input and arguments | 8 |
| Bash | `bash-012` | Handle signals properly | 7 |
| C# | `cs-004` | Use async/await properly | 9 |
| C# | `cs-012` | Handle exceptions properly | 8 |
| Docker Compose | `docker-compose-003` | Declare service healthchecks | 7 |
| Dockerfile | `dockerfile-004` | Declare HEALTHCHECK for production images | 7 |
| GitHub Actions | `gha-008` | Set timeout-minutes on jobs | 6 |
| Go | `go-001` | Errors are values | 9 |
| Go | `go-017` | Handle every error path | 9 |
| JavaScript | `js-001` | Avoid callback hell | 8 |
| JavaScript | `js-007` | Handle errors explicitly | 9 |
| PowerShell | `ps-002` | Use proper error handling | 9 |
| PowerShell | `ps-008` | Use -WhatIf and -Confirm support | 8 |
| PowerShell | `ps-010` | Validate parameters properly | 8 |
| PowerShell | `ps-015` | Handle null values explicitly | 7 |
| Python | `python-008` | Special cases aren't special enough to break the rules | 6 |
| Python | `python-009` | Errors should never pass silently | 9 |
| Python | `python-014` | Errors should never pass silently | 8 |
| Python | `python-016` | Although never is often better than *right* now | 5 |
| Ruby | `ruby-011` | Prefer fail over raise for exceptions | 5 |
| Rust | `rust-001` | Avoid unwrap() and expect() in production code | 9 |
| Rust | `rust-008` | Avoid unsafe unless necessary | 9 |
| Rust | `rust-014` | Error types should implement standard error traits | 8 |
| TypeScript | `ts-004` | Always specify return types | 7 |
| TypeScript | `ts-010` | Prefer unknown over any for uncertain types | 7 |
| TypeScript | `ts-012` | Prefer for-of and array methods over index loops | 4 |
| TypeScript | `ts-013` | Prefer async/await over raw promise chains | 6 |
| TypeScript | `ts-016` | Avoid console usage in production code | 4 |
| TypeScript | `ts-018` | Use template literals instead of string concatenation | 3 |

### Meaningful Abstraction — `ZEN-RIGHT-ABSTRACTION`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-003` | Use [[ ]] over [ ] | 7 |
| C++ | `cpp-003` | Use auto for type deduction | 6 |
| C++ | `cpp-005` | Use range-based for loops | 6 |
| C++ | `cpp-009` | Follow Rule of Zero/Three/Five | 8 |
| C++ | `cpp-011` | Avoid global variables | 8 |
| C++ | `cpp-013` | Prefer std::optional over null pointers | 6 |
| C# | `cs-002` | Use expression-bodied members | 5 |
| C# | `cs-005` | Use pattern matching | 6 |
| C# | `cs-007` | Use collection expressions | 5 |
| C# | `cs-011` | Use LINQ appropriately | 7 |
| C# | `cs-013` | Use records for DTOs | 6 |
| CSS | `css-001` | Avoid specificity creep | 7 |
| CSS | `css-002` | Avoid magic pixel values | 6 |
| GitHub Actions | `gha-011` | Use GITHUB_OUTPUT instead of deprecated set-output | 7 |
| GitHub Actions | `gha-012` | Use GITHUB_STATE and GITHUB_ENV instead of deprecated commands | 7 |
| GitLab CI | `gitlab-ci-008` | Prefer rules over only/except | 6 |
| Go | `go-002` | Accept interfaces, return structs | 7 |
| Go | `go-003` | Make the zero value useful | 6 |
| Go | `go-005` | Don't use pointer to interface | 8 |
| Go | `go-007` | Use defer for cleanup | 7 |
| Go | `go-009` | Avoid package-level state | 7 |
| Go | `go-010` | Keep interfaces small | 7 |
| Go | `go-019` | Design for testability | 7 |
| JavaScript | `js-004` | Avoid global state | 9 |
| JavaScript | `js-005` | Functions should do one thing | 7 |
| JavaScript | `js-006` | Use modern ES6+ features | 6 |
| JavaScript | `js-009` | Prefer composition over inheritance | 7 |
| JavaScript | `js-010` | Keep functions pure when possible | 6 |
| JavaScript | `js-012` | Use destructuring for assignment | 5 |
| JavaScript | `js-013` | Use object spread over Object.assign | 5 |
| JavaScript | `js-015` | Limit function parameter count | 7 |
| JavaScript | `js-017` | Prefer Array.from/spread over arguments | 6 |
| JavaScript | `js-018` | No prototype mutation on built-in objects | 9 |
| LaTeX | `latex-007` | Prevent circular \input and \include chains | 8 |
| PowerShell | `ps-003` | Use cmdlet binding and parameters | 8 |
| PowerShell | `ps-007` | Use pipeline properly | 7 |
| PowerShell | `ps-013` | Return objects, not formatted text | 8 |
| Python | `python-003` | Simple is better than complex | 8 |
| Python | `python-004` | Complex is better than complicated | 7 |
| Python | `python-011` | There should be one-- and preferably only one --obvious way to do it | 6 |
| Python | `python-013` | Practicality beats purity | 5 |
| Python | `python-016` | Although never is often better than *right* now | 5 |
| Python | `python-019` | There should be one-- and preferably only one --obvious way to do it | 5 |
| Ruby | `ruby-001` | Convention over configuration | 7 |
| Ruby | `ruby-002` | DRY (Don't Repeat Yourself) | 8 |
| Ruby | `ruby-003` | Prefer blocks over lambdas/procs | 6 |
| Ruby | `ruby-004` | Avoid monkey-patching core classes | 9 |
| Ruby | `ruby-007` | Prefer symbols over strings for keys | 5 |
| Ruby | `ruby-010` | Use Ruby's expressive syntax | 6 |
| Rust | `rust-003` | Prefer iterators over loops | 7 |
| Rust | `rust-007` | Use newtype pattern for type safety | 7 |
| Rust | `rust-009` | Use std traits appropriately | 7 |
| Rust | `rust-010` | Prefer enums over booleans for state | 7 |
| Rust | `rust-012` | Avoid Rc<RefCell<T>> unless necessary | 7 |
| Rust | `rust-016` | Implement Default when there is an obvious default value | 5 |
| Rust | `rust-017` | Use From/Into for type conversions | 6 |
| TypeScript | `ts-003` | Prefer interfaces over type aliases for objects | 5 |
| TypeScript | `ts-007` | Use utility types | 6 |
| TypeScript | `ts-009` | Use enums or const assertions appropriately | 6 |
| TypeScript | `ts-011` | Use optional chaining instead of manual null checks | 5 |
| TypeScript | `ts-012` | Prefer for-of and array methods over index loops | 4 |
| TypeScript | `ts-017` | Use ES module imports instead of require() | 5 |

### Unambiguous Naming — `ZEN-UNAMBIGUOUS-NAME`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-004` | Use $() over backticks | 6 |
| Bash | `bash-011` | Use meaningful variable names | 7 |
| Bash | `bash-014` | Include usage information | 6 |
| C# | `cs-003` | Prefer var for local variables | 5 |
| C# | `cs-006` | Prefer string interpolation | 6 |
| C# | `cs-008` | Follow naming conventions | 7 |
| C# | `cs-010` | Avoid magic numbers | 6 |
| Go | `go-004` | Use short variable names | 5 |
| Go | `go-008` | Package names are singular | 5 |
| Go | `go-013` | Organize by responsibility | 6 |
| Go | `go-014` | Embed for composition, not inheritance | 7 |
| Go | `go-020` | Write self-documenting code | 5 |
| JavaScript | `js-008` | Avoid magic numbers and strings | 6 |
| JavaScript | `js-011` | Use meaningful names | 8 |
| JSON | `json-005` | Keys are case-sensitive identifiers | 5 |
| LaTeX | `latex-003` | Require captions in figures and tables | 6 |
| Markdown | `md-002` | Images require meaningful alt text | 8 |
| Markdown | `md-004` | Fence code blocks with explicit language tags | 4 |
| Markdown | `md-006` | Use named default exports in MDX | 6 |
| PowerShell | `ps-001` | Use approved verbs | 7 |
| PowerShell | `ps-004` | Use PascalCase for function names | 7 |
| PowerShell | `ps-006` | Avoid positional parameters | 7 |
| PowerShell | `ps-009` | Use splatting for readability | 6 |
| PowerShell | `ps-011` | Use comment-based help | 7 |
| PowerShell | `ps-012` | Avoid aliases in scripts | 6 |
| Python | `python-001` | Beautiful is better than ugly | 4 |
| Python | `python-006` | Sparse is better than dense | 5 |
| Python | `python-007` | Readability counts | 9 |
| Python | `python-012` | Namespaces are one honking great idea | 7 |
| Python | `python-017` | If the implementation is hard to explain, it's a bad idea | 6 |
| Python | `python-018` | If the implementation is easy to explain, it may be a good idea | 3 |
| Ruby | `ruby-005` | Use meaningful method names with ?/! convention | 7 |
| Ruby | `ruby-006` | Keep method chains readable | 6 |
| Ruby | `ruby-007` | Prefer symbols over strings for keys | 5 |
| Rust | `rust-015` | Follow Rust naming conventions (RFC 430) | 6 |
| SQL | `sql-007` | Use descriptive table aliases | 4 |
| SQL | `sql-009` | Prefer explicit JOIN syntax over ANSI-89 comma joins | 6 |
| TOML | `toml-001` | Avoid inline tables | 6 |
| TOML | `toml-004` | Avoid trailing commas | 5 |
| TypeScript | `ts-003` | Prefer interfaces over type aliases for objects | 5 |
| TypeScript | `ts-014` | Prefer named exports over default exports | 4 |
| TypeScript | `ts-018` | Use template literals instead of string concatenation | 3 |
| XML | `xml-003` | Namespaces prevent local collisions | 6 |
| YAML | `yaml-001` | Use consistent indentation | 6 |
| YAML | `yaml-002` | Avoid tabs in indentation | 7 |
| YAML | `yaml-005` | Keys should be self-explanatory | 5 |
| YAML | `yaml-007` | Comments explain intent | 4 |

### Visible State — `ZEN-VISIBLE-STATE`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-009` | Use readonly for constants | 6 |
| C++ | `cpp-002` | Prefer smart pointers over raw pointers | 9 |
| C++ | `cpp-006` | Avoid manual memory allocation | 9 |
| C++ | `cpp-011` | Avoid global variables | 8 |
| C# | `cs-002` | Use expression-bodied members | 5 |
| C# | `cs-009` | Use IDisposable and using statements | 9 |
| C# | `cs-010` | Avoid magic numbers | 6 |
| GitHub Actions | `gha-012` | Use GITHUB_STATE and GITHUB_ENV instead of deprecated commands | 7 |
| Go | `go-006` | Avoid goroutine leaks | 9 |
| Go | `go-009` | Avoid package-level state | 7 |
| Go | `go-011` | Use context for cancellation | 8 |
| Go | `go-015` | Communicate by sharing memory through channels | 8 |
| Go | `go-019` | Design for testability | 7 |
| Go | `go-020` | Write self-documenting code | 5 |
| JavaScript | `js-002` | Prefer const over let, never var | 7 |
| JavaScript | `js-004` | Avoid global state | 9 |
| JavaScript | `js-010` | Keep functions pure when possible | 6 |
| JavaScript | `js-014` | Avoid with statement | 9 |
| Python | `python-006` | Sparse is better than dense | 5 |
| Python | `python-011` | There should be one-- and preferably only one --obvious way to do it | 6 |
| Rust | `rust-002` | Use the type system to prevent bugs | 8 |
| Rust | `rust-010` | Prefer enums over booleans for state | 7 |
| Rust | `rust-011` | Use lifetimes judiciously | 6 |
| Rust | `rust-012` | Avoid Rc<RefCell<T>> unless necessary | 7 |
| Rust | `rust-013` | Send + Sync should be implemented when types allow | 7 |
| Rust | `rust-016` | Implement Default when there is an obvious default value | 5 |
| SQL | `sql-002` | Always include INSERT column lists | 7 |
| TypeScript | `ts-005` | Use readonly when appropriate | 6 |

### Strict Fences — `ZEN-STRICT-FENCES`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| Bash | `bash-006` | Use functions for reusable code | 6 |
| Bash | `bash-007` | Use local variables in functions | 7 |
| Bash | `bash-008` | Avoid eval | 9 |
| C++ | `cpp-001` | Use RAII for resource management | 9 |
| C# | `cs-009` | Use IDisposable and using statements | 9 |
| CSS | `css-004` | Keep stylesheets modular | 5 |
| Docker Compose | `docker-compose-001` | Avoid latest tags in image definitions | 8 |
| Docker Compose | `docker-compose-002` | Run services as non-root user | 9 |
| Docker Compose | `docker-compose-004` | Keep secrets out of environment literals | 9 |
| Dockerfile | `dockerfile-001` | Avoid latest tags in base images | 8 |
| Dockerfile | `dockerfile-002` | Run containers as non-root user | 9 |
| Dockerfile | `dockerfile-006` | Keep secrets out of ENV and ARG instructions | 9 |
| GitHub Actions | `gha-001` | Pin third-party actions by full commit SHA | 9 |
| GitHub Actions | `gha-002` | Avoid pull_request_target checkout of untrusted head SHA | 10 |
| GitHub Actions | `gha-003` | Do not expose secrets in run blocks | 10 |
| GitHub Actions | `gha-004` | Avoid over-permissive or missing workflow permissions | 8 |
| GitHub Actions | `gha-005` | Restrict GITHUB_TOKEN permissions per job | 7 |
| GitHub Actions | `gha-006` | Split oversized workflows | 5 |
| GitHub Actions | `gha-015` | Set artifact retention explicitly | 4 |
| GitLab CI | `gitlab-ci-001` | Pin container image tags | 8 |
| GitLab CI | `gitlab-ci-002` | Avoid exposed variables in repository YAML | 8 |
| GitLab CI | `gitlab-ci-003` | Use allow_failure only with rules-based context | 6 |
| Go | `go-008` | Package names are singular | 5 |
| Go | `go-013` | Organize by responsibility | 6 |
| JavaScript | `js-016` | No eval() | 9 |
| LaTeX | `latex-004` | Maintain bibliography hygiene | 6 |
| LaTeX | `latex-009` | Remove unused packages | 5 |
| Markdown | `md-007` | Keep MDX imports hygienic | 5 |
| PowerShell | `ps-014` | Use script scope carefully | 7 |
| Python | `python-012` | Namespaces are one honking great idea | 7 |
| SQL | `sql-003` | Prefer parameterized SQL over dynamic concatenation | 9 |
| TOML | `toml-006` | Order implies importance | 4 |
| TypeScript | `ts-014` | Prefer named exports over default exports | 4 |
| XML | `xml-003` | Namespaces prevent local collisions | 6 |

### Proportionate Complexity — `ZEN-PROPORTIONATE-COMPLEXITY`

| Language | Rule ID | Principle | Severity |
|----------|---------|-----------|:--------:|
| C++ | `cpp-010` | Use std::move for rvalue references | 7 |
| C# | `cs-002` | Use expression-bodied members | 5 |
| C# | `cs-006` | Prefer string interpolation | 6 |
| C# | `cs-013` | Use records for DTOs | 6 |
| CSS | `css-005` | Prefer modern import strategy | 6 |
| Dockerfile | `dockerfile-005` | Use multi-stage builds for compiled workloads | 6 |
| Dockerfile | `dockerfile-007` | Maintain layer discipline | 5 |
| GitHub Actions | `gha-009` | Use concurrency controls to cancel stale runs | 5 |
| GitHub Actions | `gha-014` | Cache dependencies for installation-heavy steps | 4 |
| GitLab CI | `gitlab-ci-006` | Use interruptible pipelines | 5 |
| GitLab CI | `gitlab-ci-007` | Model job DAG dependencies with needs | 5 |
| GitLab CI | `gitlab-ci-009` | Cache dependency installs | 5 |
| Go | `go-016` | Avoid unnecessary complexity | 7 |
| Go | `go-018` | Avoid premature optimization | 5 |
| Python | `python-003` | Simple is better than complex | 8 |
| Python | `python-004` | Complex is better than complicated | 7 |
| Python | `python-013` | Practicality beats purity | 5 |
| Python | `python-018` | If the implementation is easy to explain, it may be a good idea | 3 |
| Ruby | `ruby-003` | Prefer blocks over lambdas/procs | 6 |
| Ruby | `ruby-009` | Avoid needless metaprogramming | 8 |
| Rust | `rust-004` | Clone sparingly | 7 |
| SQL | `sql-001` | Never use SELECT * | 6 |
| SQL | `sql-005` | Avoid implicit type coercion in JOIN predicates | 6 |
| SQL | `sql-006` | Bound result sets with WHERE/LIMIT/TOP | 5 |
| TypeScript | `ts-003` | Prefer interfaces over type aliases for objects | 5 |
