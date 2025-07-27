
print("""
███╗   ███╗ █████╗  ██████╗        ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗██╗
████╗ ████║██╔══██╗██╔════╝       ██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║██║
██╔████╔██║███████║██║            ██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║██║
██║╚██╔╝██║██╔══██║██║    ████    ██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║
██║ ╚═╝ ██║██║  ██║╚██████╗       ╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚████║██║
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝        ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝

████████╗██████╗  █████╗ ███╗   ██╗███████╗ ██████╗██████╗ ██╗██████╗ ████████╗
╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝██╔══██╗██║██╔══██╗╚══██╔══╝
   ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ██████╔╝██║██████╔╝   ██║   
   ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██╗██║██╔═══╝    ██║   
   ██║   ██║  ██║██║  ██║██║ ╚████║███████║╚██████╗██║  ██║██║██║        ██║   
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   

                 macOS Gemini AI Transcription Tool 
                          Version 2025.07.27
""")


import google.generativeai as genai
import os
import pathlib
import re # 正規表現を使うために必要です
import json # JSONファイルを読み込むために必要です

# APIキーをJSONファイルから読み込む
CONFIG_FILE = 'config.json'

# Configuration file for interactive inputs
INTERACTIVE_CONFIG_FILE = 'interactive_config.json'

def load_interactive_config():
    if os.path.exists(INTERACTIVE_CONFIG_FILE):
        with open(INTERACTIVE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_interactive_config(config):
    with open(INTERACTIVE_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

try:
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    api_key = config.get('GEMINI_API_KEY')
    model_name = config.get('GEMINI_MODEL', 'gemini-1.5-flash') # デフォルトモデルを設定
    if not api_key:
        raise ValueError(f"'{CONFIG_FILE}'に'GEMINI_API_KEY'が設定されていません。")
    genai.configure(api_key=api_key)
    print(f"APIキーを'{CONFIG_FILE}'から正常に読み込みました。")
    print(f"使用するGeminiモデル: {model_name}")
except FileNotFoundError:
    print(f"エラー: 設定ファイル'{CONFIG_FILE}'が見つかりません。")
    print(f"'{CONFIG_FILE}'を作成し、以下のようにAPIキーを設定してください:")
    print("{\n    \"GEMINI_API_KEY\": \"YOUR_GEMINI_API_KEY\"\n}")
    exit(1)
except json.JSONDecodeError:
    print(f"エラー: '{CONFIG_FILE}'のJSON形式が不正です。")
    exit(1)
except ValueError as e:
    print(f"エラー: {e}")
    exit(1)

def correct_and_convert_chunk(text_chunk, theme, speaker_attribute, purpose, tone, model_name):

    """
    一つのテキストチャンクをGemini APIに送り、誤字脱字修正と話し言葉から書き言葉への変換を行います。
    """
    model = genai.GenerativeModel(model_name) # 使用するGeminiモデルを指定

    prompt = f"""### 役割
あなたはプロの聞き起こし編集者です。

### 依頼事項
以下はYouTube動画のトランスクリプトと、事前情報です。この情報をもとに、トランスクリプトを正確に理解し、話し言葉から自然な書き言葉に変換してください。

### 事前情報
動画のテーマ: {theme}
話者の属性: 専門家（{speaker_attribute}）
動画の目的: {purpose}
出力のトーン: {tone}

### 参照
誤字脱字を修正し、話し言葉を自然な書き言葉に変換してください。
元の内容の意味は変えないでください。間投詞（「えー」「あのー」など）や繰り返しの表現は、必要に応じて削除または簡潔にまとめてください。
句読点や改行を適切に追加し、読者が読みやすいように整形してください。
修正後の文章のみを出力してください。余計な説明は不要です。

### トランスクリプト
{text_chunk}
"""
    try:
        response = model.generate_content(prompt)
        # 応答が複数のパーツに分かれている場合があるため、text属性で結合します
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API呼び出し中にエラーが発生しました: {e}")
        return f"[エラー: このチャンクの処理に失敗しました - {text_chunk}]"

if __name__ == "__main__":
    interactive_config = load_interactive_config()

    # 1. 対象ファイルのパスを指定してください
    input_file_path = input("1. 対象ファイルのパスを指定してください: ").strip().strip("'")
    if input_file_path.lower() == 'q':
        exit(0)
    while not os.path.exists(input_file_path):
        print("エラー: 指定されたファイルが見つかりません。")
        input_file_path = input("1. 対象ファイルのパスを指定してください: ").strip().strip("'")
        if input_file_path.lower() == 'q':
            exit(0)

    # 2. 動画のテーマを入力してください
    default_theme = interactive_config.get('theme', '')
    theme = input(f"2. 動画のテーマを入力してください (現在: {default_theme}): ").strip()
    if theme.lower() == 'q':
        exit(0)
    if not theme:
        theme = default_theme
    interactive_config['theme'] = theme

    # 3. 話者の属性・専門家を入力してください
    default_speaker_attribute = interactive_config.get('speaker_attribute', '')
    speaker_attribute = input(f"3. 話者の属性・専門家を入力してください (現在: {default_speaker_attribute}): ").strip()
    if speaker_attribute.lower() == 'q':
        exit(0)
    if not speaker_attribute:
        speaker_attribute = default_speaker_attribute
    interactive_config['speaker_attribute'] = speaker_attribute

    # 4. 動画の目的を入力してください
    default_purpose = interactive_config.get('purpose', '')
    purpose = input(f"4. 動画の目的を入力してください (現在: {default_purpose}): ").strip()
    if purpose.lower() == 'q':
        exit(0)
    if not purpose:
        purpose = default_purpose
    interactive_config['purpose'] = purpose

    # 5. 出力のトーンを入力してください
    default_tone = interactive_config.get('tone', '')
    tone = input(f"5. 出力のトーンを入力してください (現在: {default_tone}): ").strip()
    if tone.lower() == 'q':
        exit(0)
    if not tone:
        tone = default_tone
    interactive_config['tone'] = tone

    save_interactive_config(interactive_config)

    # 出力ファイル名の生成
    input_path_obj = pathlib.Path(input_file_path)
    output_file_name = f"{input_path_obj.stem}_修正{input_path_obj.suffix}"
    output_file_path = input_path_obj.parent / output_file_name

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            full_text = f_in.read()
            # タイムスタンプを削除 (例: (00:18))
            full_text = re.sub(r'\(\d{2}:\d{2}\)', '', full_text)

        min_chunk_size = 3000
        max_chunk_size = 3500
        current_pos = 0
        chunk_num = 0

        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            while current_pos < len(full_text):
                chunk_num += 1
                end_pos = min(current_pos + max_chunk_size, len(full_text))

                # チャンクの終わりを調整して、単語の途中や文の途中で切れないようにする
                # ただし、min_chunk_sizeを下回らないようにする
                if end_pos < len(full_text):
                    # 理想的には句読点や改行で区切る
                    # ここでは、max_chunk_sizeを超えない範囲で、最後のスペースまたは句読点を探す
                    # もし見つからなければ、max_chunk_sizeで強制的に区切る
                    search_end = min(current_pos + max_chunk_size, len(full_text))
                    break_points = [m.end() for m in re.finditer(r'[.!?。！？\n\s]', full_text[current_pos:search_end])]
                    
                    best_break_point = -1
                    for bp in break_points:
                        if current_pos + bp >= current_pos + min_chunk_size:
                            best_break_point = bp
                            break
                    
                    if best_break_point != -1:
                        end_pos = current_pos + best_break_point
                    else:
                        # 適切な区切りが見つからない場合、max_chunk_sizeで強制的に区切る
                        end_pos = min(current_pos + max_chunk_size, len(full_text))
                
                # チャンクがmin_chunk_sizeより小さい場合は、次のチャンクと結合するか、強制的にそのサイズにする
                # ここでは、単純にmin_chunk_sizeを下回らないように調整
                if end_pos - current_pos < min_chunk_size and end_pos < len(full_text):
                    end_pos = min(current_pos + max_chunk_size, len(full_text))


                text_chunk = full_text[current_pos:end_pos].strip()
                if not text_chunk:
                    current_pos = end_pos
                    continue

                print(f"--- チャンク {chunk_num} を処理中 (サイズ: {len(text_chunk)} 文字) ---")
                processed_chunk = correct_and_convert_chunk(text_chunk, theme, speaker_attribute, purpose, tone, model_name)
                f_out.write(processed_chunk)
                f_out.write("\n\n") # 各チャンクの処理結果の間に空行を入れる

                current_pos = end_pos

    except FileNotFoundError:
        print(f"エラー: 入力ファイル'{input_file_path}'または出力ファイル'{output_file_path}'が見つかりません。")
        exit(1)
    except Exception as e:
        print(f"ファイル処理中にエラーが発生しました: {e}")
        exit(1)