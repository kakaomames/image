from flask import Flask, request, send_from_directory, Response, jsonify
import subprocess
import os
import xmltodict # XMLをJSONに変換するためにインポート (pip install xmltodict が必要)

app = Flask(__name__, static_folder='static', template_folder='templates')

# CORSを許可するためのヘッダー
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.after_request
def after_request(response):
    return add_cors_headers(response)

# ルートパス ("/") で index.html を返す (変更なし)
@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

# "/jimaku?id=videoid" で、curlの結果を字幕データとして返すAPIエンドポイント (変更なし)
@app.route('/jimaku')
def get_captions():
    video_id = request.args.get('id')
    if not video_id:
        return Response("Video ID is required.", status=400)

    captions_url = f"https://inv.nadeko.net/api/v1/captions/{video_id}?label=Japanese%20(auto-generated)"
    curl_command = ["curl", "-sS", "--compressed", captions_url]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        return Response(result.stdout, mimetype="text/vtt")
    except subprocess.CalledProcessError as e:
        return Response(f"Error fetching captions with curl: {e.stderr}", status=500)
    except FileNotFoundError:
        return Response("Curl command not found. Please ensure curl is installed and in your PATH.", status=500)
    except Exception as e:
        return Response(f"An unexpected error occurred: {e}", status=500)

# 新しいエンドポイント: "/link?id=${videoid}" でXMLをJSONに変換して返す
@app.route('/link')
def get_dash_manifest_as_json():
    video_id = request.args.get('id')
    if not video_id:
        return Response("Video ID is required.", status=400)

    # DASHマニフェストを取得するためのURL
    dash_manifest_url = f"https://inv-eu3-c.nadeko.net/api/manifest/dash/id/{video_id}?check="
    curl_command = ["curl", "-sS", "--compressed", dash_manifest_url]

    try:
        # curlコマンドを実行し、XML出力を取得
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        xml_string = result.stdout

        # XMLをJSONに変換
        # parse_xml_to_json 関数を定義するか、xmltodictを使う
        json_data = xmltodict.parse(xml_string) # xmltodictを使用

        # JSONレスポンスとして返す
        return jsonify(json_data)
    except subprocess.CalledProcessError as e:
        return Response(f"Error fetching DASH manifest with curl: {e.stderr}", status=500)
    except FileNotFoundError:
        return Response("Curl command not found. Please ensure curl is installed and in your PATH.", status=500)
    except Exception as e:
        # XMLパースエラーなどもここで捕捉
        return Response(f"An unexpected error occurred during XML parsing or fetching: {e}", status=500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
