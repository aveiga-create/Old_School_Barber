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

  // Botões de Abrir
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

  // Botões de Fechar (o "X")
  document
    .getElementById("close-login")
    ?.addEventListener("click", fecharModais);
  document
    .getElementById("close-cadastro")
    ?.addEventListener("click", fecharModais);

  // Fechar ao clicar fora da caixinha do modal
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

  // Envio do Login
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

  // Envio do Cadastro
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
});
