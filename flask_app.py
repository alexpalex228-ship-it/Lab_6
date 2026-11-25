from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Лабораторная работа № 6 — Flask</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; max-width: 700px; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
        th { background-color: #f4f4f4; }
        .greeting { margin-top: 15px; font-weight: bold; color: #1a5f7a; }
    </style>
</head>
<body>
    <h1>Форма приветствия</h1>
    <form method="POST">
        <label for="username">Введите ваше имя:</label>
        <input type="text" id="username" name="username" required>
        <button type="submit">Поприветствовать</button>
    </form>

    {% if greeting %}
        <div class="greeting">{{ greeting }}</div>
    {% endif %}

    <h2>Таблица данных</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Группа</th>
                <th>Курс</th>
            </tr>
        </thead>
        <tbody>
            {% for row in students %}
            <tr>
                <td>{{ row.id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.group }}</td>
                <td>{{ row.course }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

STUDENTS_DATA = [
    {"id": 1, "name": "Алексей", "group": "ИВТ-21", "course": 3},
    {"id": 2, "name": "Мария", "group": "ИВТ-21", "course": 3},
    {"id": 3, "name": "Дмитрий", "group": "ИВТ-22", "course": 2},
]


@app.route("/", methods=["GET", "POST"])
def index():
    greeting = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if username:
            greeting = f"Привет, {username}! Добро пожаловать в веб-приложение."
    return render_template_string(HTML_TEMPLATE, greeting=greeting, students=STUDENTS_DATA)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)