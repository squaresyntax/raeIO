"""Entry point for launching the Streamlit UI."""

import sys
import streamlit.web.cli as stcli


def main() -> int:
    """Launch the Streamlit UI via Streamlit's CLI."""
    # Replicate ``streamlit run ui.py`` without spawning a subshell.
    sys.argv = ["streamlit", "run", "ui.py"]
    return stcli.main()


if __name__ == "__main__":
    raise SystemExit(main())
