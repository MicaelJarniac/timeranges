<div align="center">

  [![Discord][badge-chat]][chat]
  <br>
  <br>

  | | ![Badges][label-badges] |
  |--|--|
  | ![Build][label-build] | [![Python package][badge-actions]][actions] [![semantic-release][badge-semantic-release]][semantic-release] [![PyPI][badge-pypi]][pypi] [![Read the Docs][badge-docs]][docs] |
  | ![Tests][label-tests] | [![coverage][badge-coverage]][coverage] [![pre-commit][badge-pre-commit]][pre-commit] |
  | ![Standards][label-standards] | [![SemVer 2.0.0][badge-semver]][semver] [![Conventional Commits][badge-conventional-commits]][conventional-commits] |
  | ![Code][label-code] | [![Code style: black][badge-black]][Black] [![Imports: isort][badge-isort]][isort] [![Checked with mypy][badge-mypy]][mypy] |
  | ![Repo][label-repo] | [![GitHub issues][badge-issues]][issues] [![GitHub stars][badge-stars]][stars] [![GitHub license][badge-license]][license] [![All Contributors][badge-all-contributors]][contributors] [![Contributor Covenant][badge-code-of-conduct]][code-of-conduct] |
</div>

<!-- Badges -->
[badge-chat]: https://img.shields.io/discord/269146666441900032?label=chat&logo=discord&style=flat-square
[chat]: https://discord.gg/6Q5XW5H

<!-- Labels -->
[label-badges]: https://img.shields.io/badge/%F0%9F%94%96-badges-purple?style=for-the-badge
[label-build]: https://img.shields.io/badge/%F0%9F%94%A7-build-darkblue?style=flat-square
[label-tests]: https://img.shields.io/badge/%F0%9F%A7%AA-tests-darkblue?style=flat-square
[label-standards]: https://img.shields.io/badge/%F0%9F%93%91-standards-darkblue?style=flat-square
[label-code]: https://img.shields.io/badge/%F0%9F%92%BB-code-darkblue?style=flat-square
[label-repo]: https://img.shields.io/badge/%F0%9F%93%81-repo-darkblue?style=flat-square

<!-- Build -->
[badge-actions]: https://img.shields.io/github/workflow/status/MicaelJarniac/timeranges/Python%20package/main?style=flat-square
[actions]: https://github.com/MicaelJarniac/timeranges/actions
[badge-semantic-release]: https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079?style=flat-square
[semantic-release]: https://github.com/semantic-release/semantic-release
[badge-pypi]: https://img.shields.io/pypi/v/timeranges?style=flat-square
[pypi]: https://pypi.org/project/timeranges
[badge-docs]: https://img.shields.io/readthedocs/timeranges?style=flat-square
[docs]: https://timeranges.readthedocs.io

<!-- Tests -->
[badge-coverage]: https://img.shields.io/codecov/c/gh/MicaelJarniac/timeranges?logo=codecov&style=flat-square&token=yqKa1DPwPC
[coverage]: https://codecov.io/gh/MicaelJarniac/timeranges
[badge-pre-commit]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white
[pre-commit]: https://github.com/pre-commit/pre-commit

<!-- Standards -->
[badge-semver]: https://img.shields.io/badge/SemVer-2.0.0-blue?style=flat-square&logo=semver
[semver]: https://semver.org/spec/v2.0.0.html
[badge-conventional-commits]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow?style=flat-square
[conventional-commits]: https://conventionalcommits.org

<!-- Code -->
[badge-black]: https://img.shields.io/badge/code%20style-black-black?style=flat-square
[Black]: https://github.com/psf/black
[badge-isort]: https://img.shields.io/badge/imports-isort-%231674b1?style=flat-square&labelColor=ef8336
[isort]: https://pycqa.github.io/isort
[badge-mypy]: https://img.shields.io/badge/mypy-checked-2A6DB2?style=flat-square
[mypy]: http://mypy-lang.org

<!-- Repo -->
[badge-issues]: https://img.shields.io/github/issues/MicaelJarniac/timeranges?style=flat-square
[issues]: https://github.com/MicaelJarniac/timeranges/issues
[badge-stars]: https://img.shields.io/github/stars/MicaelJarniac/timeranges?style=flat-square
[stars]: https://github.com/MicaelJarniac/timeranges/stargazers
[badge-license]: https://img.shields.io/github/license/MicaelJarniac/timeranges?style=flat-square
[license]: https://github.com/MicaelJarniac/timeranges/blob/main/LICENSE
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[badge-all-contributors]: https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[contributors]: #Contributors-✨
[badge-code-of-conduct]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa?style=flat-square
[code-of-conduct]: CODE_OF_CONDUCT.md
<!---->

# timeranges
Time ranges.

[Read the Docs][docs]

## Installation

### pip
[*timeranges*][pypi] is available on [pip](https://pip.pypa.io/en/stable/):

```bash
pip install timeranges
```

### GitHub
You can also install the latest version of the code directly from GitHub:
```bash
pip install git+git://github.com/MicaelJarniac/timeranges
```

## Usage
For more examples, see the [full documentation][docs].

### TimeRange
```python
from datetime import time

from timeranges import TimeRange


# Create a `TimeRange` instance with the interval "0:00 -> 10:00"
time_range = TimeRange(time(0), time(10))

# Check if these times are contained in `time_range`
assert time(0) in time_range
assert time(5) in time_range
assert time(10) in time_range

# Check if these times aren't contained in `time_range`
assert time(10, 0, 1) not in time_range
assert time(11) not in time_range
assert time(20) not in time_range
```

### TimeRanges

```python
from datetime import time

from timeranges import TimeRange, TimeRanges


# Create some `TimeRange` instances
time_range_1 = TimeRange(time(0), time(10))
time_range_2 = TimeRange(time(15), time(20))

# Create a `TimeRanges` instance containing multiple `TimeRange`
time_ranges = TimeRanges([time_range, time_range_2])

assert time(0) in time_ranges
assert time(5) in time_ranges
assert time(10) in time_ranges
assert time(12) not in time_ranges
assert time(15) in time_ranges
assert time(17) in time_ranges
assert time(20) in time_ranges
assert time(22) not in time_ranges
```

### WeekRange
```python
from datetime import time, datetime

from timematic.enums import Weekday
from timeranges import TimeRange, TimeRanges, WeekRange

week_range = WeekRange(
    {
        Weekday.MONDAY: TimeRanges(
            [
                TimeRange(time(5), time(10)),
                TimeRange(time(12), time(14)),
            ]
        ),
        Weekday.SATURDAY: TimeRanges(
            [
                TimeRange(time(0), time(2)),
                TimeRange(time(4), time(8)),
            ]
        )
    }
)

assert datetime(2021, 12, 6, 5, 0, 0) in week_range
assert datetime(2021, 12, 6, 8, 0, 0) in week_range
assert datetime(2021, 12, 6, 10, 0, 0) in week_range
assert datetime(2021, 12, 6, 11, 0, 0) not in week_range
assert datetime(2021, 12, 7, 5, 0, 0) not in week_range
assert datetime(2021, 12, 13, 5, 0, 0) in week_range
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

More details can be found in [CONTRIBUTING](CONTRIBUTING.md).

## Contributors ✨
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/MicaelJarniac"><img src="https://avatars.githubusercontent.com/u/19514231?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Micael Jarniac</b></sub></a><br /><a href="https://github.com/MicaelJarniac/timeranges/issues?q=author%3AMicaelJarniac" title="Bug reports">🐛</a> <a href="https://github.com/MicaelJarniac/timeranges/commits?author=MicaelJarniac" title="Code">💻</a> <a href="https://github.com/MicaelJarniac/timeranges/commits?author=MicaelJarniac" title="Documentation">📖</a> <a href="#example-MicaelJarniac" title="Examples">💡</a> <a href="#ideas-MicaelJarniac" title="Ideas, Planning, & Feedback">🤔</a> <a href="#maintenance-MicaelJarniac" title="Maintenance">🚧</a> <a href="#projectManagement-MicaelJarniac" title="Project Management">📆</a> <a href="https://github.com/MicaelJarniac/timeranges/pulls?q=is%3Apr+reviewed-by%3AMicaelJarniac" title="Reviewed Pull Requests">👀</a> <a href="#tool-MicaelJarniac" title="Tools">🔧</a> <a href="https://github.com/MicaelJarniac/timeranges/commits?author=MicaelJarniac" title="Tests">⚠️</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License
[MIT](LICENSE)

Created from [cookiecutter-python-project](https://github.com/MicaelJarniac/cookiecutter-python-project).
