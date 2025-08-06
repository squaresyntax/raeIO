import base64
import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from raeio_agent import RAEIOAgent
from browser_automation import STEALTH_UA


def base_config(tmp_path):
    return {
        'memory_path': str(tmp_path / 'memory.jsonl'),
        'temp_dir': str(tmp_path / 'temp'),
        'cache_dir': str(tmp_path / 'cache'),
        'tts_cache_dir': str(tmp_path / 'tts'),
        'plugin_dir': str(tmp_path / 'plugins'),
        'browser_headless': False,
    }


def test_task_memory_encryption(tmp_path):
    cfg = base_config(tmp_path)
    cfg['fuckery_mode'] = True
    agent = RAEIOAgent(cfg, logger=None)
    agent.memory.log_task('test', 'hello', {}, 'out', True, 0.1)
    with open(cfg['memory_path'], 'r') as f:
        line = f.readline().strip()
    assert not line.startswith('{')
    decoded = json.loads(base64.b64decode(line).decode())
    assert decoded['prompt'] == 'hello'


def test_browser_stealth_mode(tmp_path):
    cfg = base_config(tmp_path)
    cfg['fuckery_mode'] = True
    agent = RAEIOAgent(cfg, logger=None)
    assert agent.browser_automation.headless is True
    assert agent.browser_automation.user_agent == STEALTH_UA


def test_plugin_restriction(tmp_path):
    cfg = base_config(tmp_path)
    plugin_dir = tmp_path / 'plugins'
    plugin_dir.mkdir()
    plugin_file = plugin_dir / 'sample.py'
    plugin_file.write_text('def run(**kwargs):\n    return "ok"\n')

    cfg['plugin_dir'] = str(plugin_dir)

    agent_no = RAEIOAgent(cfg, logger=None)
    assert agent_no.plugin_registry.execute_plugin('sample') == 'ok'

    cfg['fuckery_mode'] = True
    agent_yes = RAEIOAgent(cfg, logger=None)
    with pytest.raises(PermissionError):
        agent_yes.plugin_registry.execute_plugin('sample')
