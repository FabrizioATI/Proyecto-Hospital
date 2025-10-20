/* script.js — versión compatible con tu clase SoftMinimalismLoginForm */

(function () {
  "use strict";

  class SoftMinimalismLoginForm {
    constructor() {
      // Detecta el form de login de forma tolerante
      this.form =
        document.querySelector('form[action*="login"][method="post" i]') ||
        document.querySelector('form input[type="password"]')?.form ||
        document.querySelector("form");

      if (!this.form) {
        console.warn("[login] No se encontró form de login.");
        return;
      }

      // Campos típicos
      this.emailInput =
        this.form.querySelector('input[name="username"]') ||
        this.form.querySelector('input[name="email"]') ||
        this.form.querySelector('input[name="correo"]') ||
        this.form.querySelector('input[type="text"], input[type="email"]');

      this.passwordInput =
        this.form.querySelector('input[name="password"], input[type="password"]');

      // Botón submit
      this.submitBtn =
        this.form.querySelector('button[type="submit"], input[type="submit"]') ||
        Array.from(this.form.querySelectorAll("button, input[type='button'], input[type='submit']"))
          .find((b) => /iniciar|entrar|acceder|login|ingresar/i.test((b.value || b.textContent || "")))
        || this.form.querySelector("button, input[type='submit']");

      // Caja de error (si no existe, se crea una oculta que no rompe diseño)
      this.errorBox =
        document.querySelector("#error-text, .error, .alert-danger, .alert-error") ||
        this.form.querySelector("#error-text, .error, .alert-danger, .alert-error") ||
        this.createErrorBox();

      // ¿Usar fetch/AJAX? Por defecto NO (dejamos que Django redirija solo)
      this.useFetch = this.form.dataset.useFetch === "true" ? true : false;

      this.bind();
    }

    createErrorBox() {
      const el = document.createElement("div");
      el.id = "login-error-autogen";
      el.style.display = "none";
      el.style.color = "red";
      el.setAttribute("aria-live", "polite");
      // Lo ponemos antes del form para no alterar tu layout interno
      this.form.parentNode.insertBefore(el, this.form);
      return el;
    }


showError(msg) {
  let box = this.errorBox;

  if (!box || !box.parentNode) {
    if (this.form && this.form.parentNode) {
      box = document.createElement("div");
      box.id = "login-error-autogen";
      box.style.display = "none";
      box.style.color = "red";
      box.setAttribute("aria-live", "polite");
      this.form.parentNode.insertBefore(box, this.form);
      this.errorBox = box;
    } else {
      box = document.getElementById("login-error-autogen") || document.createElement("div");
      if (!box.parentNode && document.body) {
        box.id = "login-error-autogen";
        box.style.display = "none";
        box.style.color = "red";
        box.setAttribute("aria-live", "polite");
        document.body.insertBefore(box, document.body.firstChild);
      }
      this.errorBox = box;
    }
  }

  if (!this.errorBox) {
    console.warn("[login] (sin contenedor de error) ", msg);
    return;
  }

  this.errorBox.textContent = msg;
  this.errorBox.style.display = "block";
  this.errorBox.setAttribute("role", "alert");
}


    clearError() {
      if (this.errorBox) {
        this.errorBox.textContent = "";
        this.errorBox.style.display = "none";
      }
    }

    disableWhileSubmitting() {
      if (!this.submitBtn) return;
      this.submitBtn.disabled = true;
      if (this.submitBtn.tagName === "BUTTON") {
        this.submitBtn.dataset._orig = this.submitBtn.textContent || "";
        this.submitBtn.textContent = "Ingresando...";
      } else {
        this.submitBtn.dataset._orig = this.submitBtn.value || "";
        this.submitBtn.value = "Ingresando...";
      }
    }

    enableAfterSubmitting() {
      if (!this.submitBtn) return;
      this.submitBtn.disabled = false;
      const orig = this.submitBtn.dataset._orig;
      if (orig != null) {
        if (this.submitBtn.tagName === "BUTTON") this.submitBtn.textContent = orig;
        else this.submitBtn.value = orig;
        delete this.submitBtn.dataset._orig;
      }
    }

    getCsrfToken() {
      const hidden = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
      if (hidden?.value) return hidden.value;
      const c = document.cookie.split("; ").find((r) => r.startsWith("csrftoken="));
      return c ? c.split("=")[1] : "";
    }

    validateEmail(value) {
      // Mantén tu lógica, pero nunca llames showError si va a romper:
      const ok = !!value && value.length >= 1;
      if (!ok) this.showError("Ingresa tu usuario.");
      return ok;
    }

    bind() {
      // Limpia errores al escribir
      this.form.addEventListener("input", () => this.clearError(), { passive: true });

      // Manejador de submit
      this.form.addEventListener("submit", (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
      const email = (this.emailInput?.value || "").trim();
      const pwd = (this.passwordInput?.value || "").trim();

      // Validación mínima
      if (!email || !pwd) {
        e.preventDefault();
        this.showError("Ingresa usuario y contraseña.");
        return;
      }
      if (!this.validateEmail(email)) {
        e.preventDefault();
        return;
      }

      // Camino 1: envío nativo (recomendado). NO usar preventDefault.
      if (!this.useFetch && (this.form.method || "post").toLowerCase() === "post") {
        this.clearError();
        this.disableWhileSubmitting();
        return; // no evitar envío Django redirige
      }

      // Camino 2: envío por fetch (opcional)
      e.preventDefault();
      this.clearError();
      this.disableWhileSubmitting();

      const csrf = this.getCsrfToken();
      if (!csrf) {
        this.enableAfterSubmitting();
        this.showError("Falta CSRF token. Recarga la página.");
        return;
      }

      try {
        const action = this.form.getAttribute("action") || window.location.href;
        const method = (this.form.getAttribute("method") || "post").toUpperCase();
        const fd = new FormData(this.form);

        const res = await fetch(action, {
          method,
          headers: { "X-CSRFToken": csrf },
          body: fd,
          redirect: "follow",
          credentials: "same-origin",
        });

        if (res.redirected) {
          window.location.href = res.url;
          return;
        }

        if (res.status === 200) {
          this.enableAfterSubmitting();
          this.showError("Usuario o contraseña inválidos.");
          return;
        }

        this.enableAfterSubmitting();
        this.showError("Error al iniciar sesión. Código: " + res.status);
      } catch (err) {
        console.error(err);
        this.enableAfterSubmitting();
        this.showError("No se pudo iniciar sesión. Revisa tu conexión.");
      }
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    new SoftMinimalismLoginForm();
  });
})();
