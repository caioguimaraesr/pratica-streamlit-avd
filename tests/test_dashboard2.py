"""Verifica os indicadores e a interação entre filtros do dashboard 2."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_dashboard2():
    app = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    assert not at.exception, at.exception
    assert [m.value for m in at.metric] == ["1.728", "30.0%", "7.8%", "+0.0 p.p."], [(m.label, m.value) for m in at.metric]
    at.multiselect(key="kpi_safety").set_value(["low"]).run()
    assert not at.exception, at.exception
    assert [m.value for m in at.metric][:3] == ["576", "0.0%", "0.0%"]
    at.slider(key="intervalo_buying_cod").set_value((0, 0)).run()
    assert not at.exception, at.exception
    assert at.metric[0].value == "144"
    at.multiselect(key="kpi_safety").set_value([]).run()
    assert not at.exception, at.exception
    assert at.metric[0].value == "0"
    assert at.metric[1].value == "—"
    assert at.warning
    at.multiselect(key="kpi_safety").set_value(["high"]).run()
    assert not at.exception, at.exception
    assert at.metric[0].value == "144"
    print("OK: KPIs, filtros combinados, seleção vazia e recuperação.")


if __name__ == "__main__":
    test_dashboard2()