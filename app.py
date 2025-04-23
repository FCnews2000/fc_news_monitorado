import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from scraping import get_latest_headlines
from trends import get_trends
from geracao_perspectivas import GeracaoPerspectivas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "uma-chave-secreta-qualquer")

# credenciais
USER = "fcnews2000"
PASS = "Biel3265980"

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))
    
    # categoria selecionada pelo usuário
    cat = request.form.get("category") or None

    # 1) coletar manchetes
    headlines = get_latest_headlines()

    # 2) pegar trends
    trends = get_trends(cat)

    # 3) gerar perspectivas
    gerador = GeracaoPerspectivas()
    for h in headlines:
        # Adicionar categoria se não existir
        if "categoria" not in h:
            h["categoria"] = cat or "geral"
        
        cap, anj = gerador._gerar_perspectivas_manuais(h["titulo"], h["categoria"])
        h["capetinha"], h["anjinho"] = cap, anj

    return render_template("index.html",
                           headlines=headlines,
                           trends=trends,
                           selected=cat)

@app.route("/api/headlines", methods=["GET"])
def api_headlines():
    """API endpoint para obter manchetes com perspectivas"""
    if "user" not in session and request.args.get("key") != app.secret_key:
        return jsonify({"error": "Não autorizado"}), 401
    
    cat = request.args.get("category")
    
    # Coletar manchetes
    headlines = get_latest_headlines()
    
    # Gerar perspectivas
    gerador = GeracaoPerspectivas()
    for h in headlines:
        # Adicionar categoria se não existir
        if "categoria" not in h:
            h["categoria"] = cat or "geral"
        
        cap, anj = gerador._gerar_perspectivas_manuais(h["titulo"], h["categoria"])
        h["capetinha"], h["anjinho"] = cap, anj
    
    return jsonify({"headlines": headlines})

@app.route("/api/trends", methods=["GET"])
def api_trends():
    """API endpoint para obter tendências"""
    if "user" not in session and request.args.get("key") != app.secret_key:
        return jsonify({"error": "Não autorizado"}), 401
    
    cat = request.args.get("category")
    trends = get_trends(cat)
    
    return jsonify({"trends": trends})

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("user")
        p = request.form.get("pass")
        if u == USER and p == PASS:
            session["user"] = u
            return redirect(url_for("home"))
        error = "Usuário ou senha incorretos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/health")
def health_check():
    """Endpoint para verificação de saúde da aplicação"""
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
