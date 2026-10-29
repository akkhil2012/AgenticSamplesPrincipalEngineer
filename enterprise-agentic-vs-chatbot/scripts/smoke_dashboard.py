from pathlib import Path
from streamlit.testing.v1 import AppTest

at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "dashboard/app.py"), default_timeout=30)
at.run()
assert not at.exception, at.exception
at.button[0].click().run()
assert not at.exception, at.exception
assert not at.error, [e.value for e in at.error]
assert at.session_state["workflow"]["status"] == "PENDING_APPROVAL"
at.selectbox[1].select("demo-approver-a").run()
next(b for b in at.button if b.label == "Submit independent decision").click().run()
assert not at.exception, at.exception
assert not at.error, [e.value for e in at.error]
assert at.session_state["workflow"]["status"] == "COMPLETED"
assert at.session_state["workflow"]["outcome"]["simulation"] is True
print("Streamlit comparison and independent approval passed against live API.")
