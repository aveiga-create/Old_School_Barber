document.addEventListener("DOMContentLoaded", function () {
  // ==========================================
  // 1. CONTROLE DOS MODAIS (ABRIR E FECHAR)
  // ==========================================
  const modalLogin = document.getElementById("modal-login");
  const modalCadastro = document.getElementById("modal-cadastro");

  function abrirModal(modal) {
    if (modal) modal.classList.add("show");
  }

  function fecharModais() {
    if (modalLogin) modalLogin.classList.remove("show");
    if (modalCadastro) modalCadastro.classList.remove("show");
  }

  document.getElementById("btn-nav-login")?.addEventListener("click", (e) => {
    e.preventDefault();
    abrirModal(modalLogin);
  });
  document.getElementById("btn-hero-login")?.addEventListener("click", (e) => {
    e.preventDefault();
    abrirModal(modalLogin);
  });
  document
    .getElementById("btn-nav-cadastro")
    ?.addEventListener("click", (e) => {
      e.preventDefault();
      abrirModal(modalCadastro);
    });

  document
    .getElementById("close-login")
    ?.addEventListener("click", fecharModais);
  document
    .getElementById("close-cadastro")
    ?.addEventListener("click", fecharModais);

  window.addEventListener("click", (e) => {
    if (e.target === modalLogin || e.target === modalCadastro) {
      fecharModais();
    }
  });

  // ==========================================
  // 2. LÓGICA DE ENVIO (FETCH API)
  // ==========================================
  const formLogin = document.getElementById("form-login");
  const formCadastro = document.getElementById("form-cadastro");

  if (formLogin) {
    formLogin.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      try {
        const response = await fetch("/login", {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            Accept: "application/json",
          },
        });

        if (!response.ok) throw new Error("Erro HTTP " + response.status);
        const data = await response.json();

        if (data.success) {
          location.reload();
        } else {
          document.getElementById("login-erro").innerText = data.message;
        }
      } catch (error) {
        console.error("Erro no login:", error);
        document.getElementById("login-erro").innerText =
          "Erro ao fazer login. Tente novamente.";
      }
    });
  }

  if (formCadastro) {
    formCadastro.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      try {
        const response = await fetch("/cadastro", {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            Accept: "application/json",
          },
        });

        if (!response.ok) throw new Error("Erro HTTP " + response.status);
        const data = await response.json();

        if (data.success) {
          alert("Cadastro realizado com sucesso!");
          location.reload();
        } else {
          document.getElementById("cadastro-erro").innerText = data.message;
        }
      } catch (error) {
        console.error("Erro no cadastro:", error);
        document.getElementById("cadastro-erro").innerText =
          "Erro ao cadastrar. Tente novamente.";
      }
    });
  }

  // ==========================================
  // 3. LÓGICA DE AGENDAMENTO (COM REGRA DE 3 HORAS E ANTI-TRAVAMENTO)
  // ==========================================
  const diasContainer = document.getElementById("diasContainer");

  // Trava de segurança: Só executa se estiver na página de agendamento
  if (diasContainer) {
    const mesAnoLabel = document.getElementById("mesAnoAtual");
    const inputData = document.getElementById("dataSelecionada");
    const inputBarbeiro = document.getElementById("barbeiroSelecionado");
    const inputHorario = document.getElementById("horarioSelecionado");
    const horariosContainer = document.getElementById("horarios");

    const meses = [
      "Janeiro",
      "Fevereiro",
      "Março",
      "Abril",
      "Maio",
      "Junho",
      "Julho",
      "Agosto",
      "Setembro",
      "Outubro",
      "Novembro",
      "Dezembro",
    ];
    const diasSemana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

    let horariosOcupados = [];
    let offsetSemana = 0;
    const hoje = new Date();

    function gerarDias() {
      diasContainer.innerHTML = "";

      let base = new Date();
      base.setDate(hoje.getDate() + offsetSemana);

      for (let i = 0; i < 7; i++) {
        let d = new Date(base);
        d.setDate(base.getDate() + i);

        if (d.getDay() === 0) continue; // Pula domingo

        // CORREÇÃO: Formatação de data manual para evitar bug de fuso horário do toISOString()
        let ano = d.getFullYear();
        let mes = String(d.getMonth() + 1).padStart(2, "0");
        let dia = String(d.getDate()).padStart(2, "0");
        let dataIso = `${ano}-${mes}-${dia}`;

        let btn = document.createElement("div");
        btn.className = "dia-card";
        btn.innerHTML = `
          <span>${diasSemana[d.getDay()]}</span>
          <strong>${dia}</strong>
        `;

        btn.onclick = () => {
          document
            .querySelectorAll(".dia-card")
            .forEach((el) => el.classList.remove("ativo"));
          btn.classList.add("ativo");

          inputData.value = dataIso;
          mesAnoLabel.innerText = `${meses[d.getMonth()]} ${ano}`;

          carregarHorarios();
        };

        diasContainer.appendChild(btn);
      }

      mesAnoLabel.innerText = `${meses[base.getMonth()]} ${base.getFullYear()}`;
    }

    document.getElementById("btn-next-data").onclick = () => {
      offsetSemana += 7;
      gerarDias();
    };

    document.getElementById("btn-prev-data").onclick = () => {
      offsetSemana -= 7;
      gerarDias();
    };

    document.querySelectorAll(".barbeiro-avatar").forEach((avatar) => {
      avatar.onclick = () => {
        document
          .querySelectorAll(".barbeiro-avatar")
          .forEach((el) => el.classList.remove("ativo"));
        avatar.classList.add("ativo");
        inputBarbeiro.value = avatar.dataset.id;
        carregarHorarios();
      };
    });

    function gerarHorariosArray() {
      const h = [];
      function add(i, f) {
        let [hh, mm] = i.split(":").map(Number);
        const [hf, mf] = f.split(":").map(Number);
        while (hh < hf || (hh === hf && mm <= mf)) {
          h.push(
            `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`,
          );
          mm += 30;
          if (mm >= 60) {
            mm = 0;
            hh++;
          }
        }
      }
      add("08:30", "12:00");
      add("13:30", "21:00");
      return h;
    }

    function renderHorarios() {
      const horarios = gerarHorariosArray();
      horariosContainer.innerHTML = "";

      // Regra: Bloqueia horários passados e exige 3h de antecedência
      const dataLimite = new Date();
      dataLimite.setHours(dataLimite.getHours() + 3);

      let encontrouHorarioLivre = false;

      horarios.forEach((h) => {
        // CORREÇÃO: Garante que horariosOcupados é um array antes de verificar (evita erro no JavaScript)
        if (Array.isArray(horariosOcupados) && horariosOcupados.includes(h))
          return;

        const [ano, mes, dia] = inputData.value.split("-").map(Number);
        const [hora, minuto] = h.split(":").map(Number);
        const dataDoSlot = new Date(ano, mes - 1, dia, hora, minuto);

        // Se o horário do botão for menor que o limite, ignora (não desenha o botão)
        if (dataDoSlot < dataLimite) return;

        encontrouHorarioLivre = true;

        const btn = document.createElement("button");
        btn.type = "button";
        btn.innerText = h;
        btn.classList.add("horario-btn");

        btn.onclick = () => {
          document
            .querySelectorAll(".horario-btn")
            .forEach((b) => b.classList.remove("selecionado"));
          btn.classList.add("selecionado");
          inputHorario.value = h;
        };

        horariosContainer.appendChild(btn);
      });

      // Se nenhum botão foi criado (tudo ocupado ou já passou do horário)
      if (!encontrouHorarioLivre) {
        horariosContainer.innerHTML =
          "<div class='caixa-aviso'><p>Nenhum horário disponível para esta data.</p></div>";
      }
    }

    function carregarHorarios() {
      if (!inputBarbeiro.value || !inputData.value) return;

      horariosContainer.innerHTML =
        "<div class='caixa-aviso'>Carregando...</div>";

      // CORREÇÃO: Adicionado tratamento de erro no fetch para não travar a tela
      fetch(
        `/horarios-ocupados?barbeiro_id=${inputBarbeiro.value}&data=${inputData.value}`,
      )
        .then((res) => {
          if (!res.ok) throw new Error("Erro de comunicação com o servidor.");

          const contentType = res.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            return res.json();
          } else {
            throw new Error(
              "Sessão expirada ou erro interno. Atualize a página.",
            );
          }
        })
        .then((data) => {
          horariosOcupados = data;
          renderHorarios();
        })
        .catch((error) => {
          console.error("Erro ao carregar horários:", error);
          horariosContainer.innerHTML = `<div class='caixa-aviso' style='color: #dc3545;'><p>${error.message}</p></div>`;
        });
    }

    gerarDias();
  }
});

// ==========================================
// 4. FUNÇÕES GLOBAIS (FORA DO DOMContentLoaded)
// ==========================================
window.cancelarAgendamento = function (id) {
  if (!confirm("Cancelar agendamento?")) return;

  fetch(`/cancelar-agendamento/${id}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        location.reload();
      } else {
        alert(data.erro || "Erro ao cancelar.");
      }
    });
};
