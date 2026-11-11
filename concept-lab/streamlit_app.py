"""Streamlit interface for this branch's offline concept lab."""
import ast
import json
from pathlib import Path
import subprocess
import sys

import streamlit as st

LAB = Path(__file__).resolve().parent
README = (LAB / 'README.md').read_text(encoding='utf-8')
TITLE = README.splitlines()[0].lstrip('# ')
DESCRIPTION = README.split('\n\n')[1]


def run_lab(arguments):
    """Run in a fresh process so reruns cannot retain demo state."""
    try:
        result = subprocess.run(
            [sys.executable, *arguments], cwd=LAB, capture_output=True,
            text=True, timeout=30, check=False,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'stdout': '', 'stderr': 'Run exceeded the 30 second limit.'}
    return {'ok': result.returncode == 0, 'stdout': result.stdout, 'stderr': result.stderr}


def test_cases():
    tree = ast.parse((LAB / 'test_main.py').read_text(encoding='utf-8'))
    return [f'test_main.{cls.name}.{method.name}'
            for cls in tree.body if isinstance(cls, ast.ClassDef)
            for method in cls.body if isinstance(method, ast.FunctionDef)
            and method.name.startswith('test_')]


st.set_page_config(page_title=TITLE, page_icon='🧪', layout='wide')
st.title(TITLE)
st.write(DESCRIPTION)
st.caption('Offline educational lab • synthetic fixtures • no API keys required')
demo_tab, tests_tab, guide_tab = st.tabs(['Run demo', 'Boundary tests', 'Guide & code'])

with demo_tab:
    st.write('Run the branch’s sample and inspect its result. Each run starts with fresh state.')
    if st.button('Run demo', type='primary'):
        with st.spinner('Running demo…'):
            st.session_state['demo_result'] = run_lab(['main.py'])
    result = st.session_state.get('demo_result')
    if result:
        if result['ok']:
            st.success('Demo completed')
            try:
                st.json(json.loads(result['stdout']))
            except json.JSONDecodeError:
                st.code(result['stdout'], language='text')
            st.download_button('Download result', result['stdout'], 'demo-result.json', 'application/json')
        else:
            st.error('Demo failed')
            st.code(result['stdout'] + result['stderr'], language='text')
        if result['ok'] and result['stderr']:
            st.code(result['stderr'], language='text')
    with st.expander('Expected example output'):
        st.json(json.loads((LAB / 'expected_output.json').read_text(encoding='utf-8')))
        st.caption('Generated identifiers may differ between runs. See the guide for the invariant being demonstrated.')

with tests_tab:
    st.write('Choose a boundary case or run the full suite to exercise success and failure behavior.')
    selected = st.selectbox('Test scenario', ['All boundary tests', *test_cases()])
    if st.button('Run tests'):
        args = ['-m', 'unittest', '-v']
        if selected != 'All boundary tests':
            args.append(selected)
        with st.spinner('Running boundary tests…'):
            st.session_state['test_result'] = (selected, run_lab(args))
    if 'test_result' in st.session_state:
        scenario, result = st.session_state['test_result']
        st.caption(f'Results for: {scenario}')
        if result['ok']:
            st.success('Tests passed')
        else:
            st.error('Tests failed')
        st.code(result['stdout'] + result['stderr'], language='text')

with guide_tab:
    st.markdown(README)
    with st.expander('Implementation'):
        st.code((LAB / 'main.py').read_text(encoding='utf-8'), language='python')
    with st.expander('Boundary test source'):
        st.code((LAB / 'test_main.py').read_text(encoding='utf-8'), language='python')
