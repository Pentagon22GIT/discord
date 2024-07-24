from flask import Flask, render_template_string
from threading import Thread

app = Flask("")

html_layout = """
<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KnowledgeBot</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap">
    <style>
        /* Reset CSS */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            line-height: 1.6;
            background-color: #f4f4f4;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            color: black;
        }

        .header-image {
            background: url('https://da2d2y78v2iva.cloudfront.net/4546/170856257032501.jpg?_=1708562570') no-repeat center center/cover;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        header h1 {
            color: #fff;
            font-size: 2.5rem;
            text-align: center;
            background: rgba(0, 0, 0, 0.5);
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }

        nav ul {
            list-style: none;
            display: flex;
            justify-content: center;
            padding: 0;
        }

        nav ul li {
            margin: 0 1rem;
        }

        nav ul li a {
            color: #fff;
            text-decoration: none;
            font-size: 1.1rem;
        }

        #hero {
            color: #fff;
            text-align: center;
            padding: 4rem 0;
        }

        #hero h2 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        #hero p {
            font-size: 1.5rem;
            margin-bottom: 2rem;
        }

        #hero .btn {
            background: #e8491d;
            color: #fff;
            padding: 0.7rem 2rem;
            text-decoration: none;
            border-radius: 5px;
            font-size: 1.1rem;
        }

        #features {
            padding: 4rem 0;
        }

        #features h2 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
        }

        .card {
            background: #fff;
            padding: 2rem;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        .card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        #commands {
            color: #fff;
            padding: 4rem 0;
            text-align: center;
        }

        #commands h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }

        #commands ul {
            list-style: none;
            padding: 0;
        }

        #commands ul li {
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }

        /* Media Queries for responsive design */
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }

            nav ul {
                flex-direction: column;
                align-items: center;
            }

            nav ul li {
                margin: 0.5rem 0;
            }

            #hero h2 {
                font-size: 2rem;
            }

            #hero p {
                font-size: 1.2rem;
            }

            #hero .btn {
                padding: 0.5rem 1.5rem;
                font-size: 1rem;
            }

            #features {
                padding: 2rem 1rem;
            }

            #features h2 {
                font-size: 2rem;
            }

            .card {
                padding: 1.5rem;
            }

            .card h3 {
                font-size: 1.3rem;
            }

            #commands {
                padding: 2rem 1rem;
            }

            #commands h2 {
                font-size: 2rem;
            }

            #commands ul li {
                font-size: 1rem;
            }
        }
    </style>
</head>

<body>
    <header>
        <div class="header-image">
            <div class="container">
                <h1>KnowledgeBot</h1>
            </div>
        </div>
    </header>
    <main>
        <section id="hero">
            <div class="container">
                <h2>日々進化し続けるBOT</h2>
                <p>「これがしたい」を叶える</p>
                <a href="#features" class="btn">詳細を見る</a>
            </div>
        </section>
        <section id="features">
            <div class="container">
                <h2>特徴</h2>
                <div class="grid">
                    <div class="card">
                        <h3>数式表示</h3>
                        <p>discordにない数式を出力する機能を保有</p>
                    </div>
                    <div class="card">
                        <h3>検索</h3>
                        <p>単語の意味や翻訳を検索できる</p>
                    </div>
                    <div class="card">
                        <h3>QRコード</h3>
                        <p>地味にめんどくさい作業を楽にしてくれる</p>
                    </div>
                </div>
            </div>
        </section>
        <section id="commands">
            <div class="container">
                <h2>コマンド</h2>
                <ul>
                    <li><code>/help</code> - 使い方を表示します。</li>
                    <li><code>/math [数式]</code> - 数式を出力</li>
                    <li><code>/define [言葉]</code> - 辞書を引きます</li>
                    <li><code>/translate [言葉] [翻訳先言語]</code> - 言語を翻訳します</li>
                    <li><code>/qrcode [URL]</code> - リンクをQRコードに変換します</li>
                    <li><code>/decode_qrcode [画像]</code> - QRコードをリンクに変換します</li>
                </ul>
            </div>
        </section>
    </main>
</body>

</html>
"""


@app.route("/")
def home():
    return render_template_string(html_layout)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()
