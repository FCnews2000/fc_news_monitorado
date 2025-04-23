import os
from flask import Flask, render_template, request, session, redirect, url_for
from scraping import get_latest_headlines  # seu scraping.py
from trends import get_trends            # seu trends.py
from geracao_perspectivas import GeracaoPerspectivas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","uma-chave-secreta-qualquer")

# credenciais
USER = "fcnews2000"
PASS = "Biel3265980"

@app.route("/", methods=["GET","POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    # categoria selecionada pelo usuário
    cat = request.form.get("category") or None

    # 1) coletar manchetes
    headlines = get_latest_headlines(cat)

    # 2) pegar trends
    trends = get_trends(cat)

    # 3) gerar perspectivas
    gerador = GeracaoPerspectivas()
    for h in headlines:
        cap, anj = gerador._gerar_perspectivas_manuais(h["titulo"], h["categoria"])
        h["capetinha"], h["anjinho"] = cap, anj

    return render_template("index.html",
                           headlines=headlines,
                           trends=trends,
                           selected=cat)


@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method=="POST":
        u = request.form.get("user")
        p = request.form.get("pass")
        if u==USER and p==PASS:
            session["user"] = u
            return redirect(url_for("home"))
        error = "Usuário ou senha incorretos"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)