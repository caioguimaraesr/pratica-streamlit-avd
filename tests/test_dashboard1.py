"""Verifica os estados de leitura e filtros do dashboard 1."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_dashboard1():
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    assert not at.exception, at.exception
    assert any("maior associação" in item.value for item in at.info)
    at.slider(key="intervalo_safety_cod").set_value((0, 0)).run()
    assert not at.exception, at.exception
    assert at.metric[0].value == "576"
    selector = next(widget for widget in at.multiselect if widget.label == "Variáveis para analisar")
    selector.set_value(["safety_cod"]).run()
    assert not at.exception, at.exception
    assert any("pelo menos 2" in item.value for item in at.warning)
    selector = next(widget for widget in at.multiselect if widget.label == "Variáveis para analisar")
    selector.set_value([]).run()
    assert not at.exception, at.exception
    assert any("pelo menos 1" in item.value for item in at.warning)
    selector = next(widget for widget in at.multiselect if widget.label == "Variáveis para analisar")
    selector.set_value(["safety_cod", "avaliacao_cod"]).run()
    at.slider(key="intervalo_safety_cod").set_value((0, 0))
    at.slider(key="intervalo_avaliacao_cod").set_value((3, 3)).run()
    assert not at.exception, at.exception
    assert any("Nenhuma configuração" in item.value for item in at.warning)
    print("OK: dashboard 1, variável constante, uma/nenhuma variável e recorte vazio.")


if __name__ == "__main__":
    test_dashboard1()