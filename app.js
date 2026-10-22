document.addEventListener("DOMContentLoaded", () => {
  const formulario = document.querySelector("form[data-calculo]");
  if (!formulario) return;

  const tipo = formulario.dataset.calculo;
  const boton = formulario.querySelector(".boton");
  const titulo = document.querySelector(".resultado h2");
  const lista = document.querySelector(".resultado ul");

  boton.addEventListener("click", async () => {
    const datos = {};
    formulario.querySelectorAll("input, select").forEach((campo) => {
      datos[campo.name] = campo.value;
    });

    try {
      const respuesta = await fetch(`/api/calcular/${tipo}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos),
      });
      const resultado = await respuesta.json();

      titulo.textContent = "Resultado";
      lista.innerHTML = "";

      const items = resultado.error
        ? [{ etiqueta: "Error", valor: resultado.error, unidad: "" }]
        : resultado.resultados;

      items.forEach((dato) => {
        const elemento = document.createElement("li");
        elemento.textContent = `${dato.etiqueta}: ${dato.valor} ${dato.unidad}`;
        lista.appendChild(elemento);
      });
    } catch (error) {
      titulo.textContent = "Error";
      lista.innerHTML = "<li>Enciende el servidor con: python app.py</li>";
    }
  });
});
