//テンプレート（textarea）にドラッグアンドドロップを実装する
//textareaにドロップしたファイル名表示
//ファイルの内容を返す


// dropされたfileをreadする
const readfileshow = (readfile, setobj) =>{
    
    new Promise((resolve, reject) => {

        const fileReader = new FileReader() ;
        fileReader.onload = function () {
            console.log( this.result ) ;
            resolve(this.result);
        };
        fileReader.readAsText( readfile ) ;

    }).then((result) => {
        insertText(setobj, '\n' + result);
        return result;
    });
};




// ドロップされたfileの拡張子をcheckする .txt .csv のみ
const extensioncheck_txt = (responseurl) =>{
    extension = responseurl.split('.').pop().toLowerCase(); 
    if (['txt', 'csv'].includes(extension)) { // 'png'～'bmp'の配列内要素がextentionに存在しているか？
        return true;
    } else {
        return false;
    }
};

//指定textareaにstringを表示させる。
const insertText = (textarea, text) => {
    const cursorPos      = textarea.selectionStart;         //textarea内のカーソル位置
    const last     = textarea.value.length;                 //文字列最終位置
    const before   = textarea.value.substr(0, cursorPos);   //挿入前の文字列
    const after    = textarea.value.substr(cursorPos, last);//挿入後の文字列
    textarea.value = before + text + after;                 //文字列をtextareaへ挿入
};

// ドロップされたファイルの内容をアップロードする処理。
//　1番目の引数はファイル単体
//　2番目はアップロード結果を反映させるテキストエリアの参照。
const upload = (uploadFile, textarea) => {
    const formData = new FormData();        // 新しいFormDataオブジェクトを作成。XmlHttoRequest関連
    formData.append('file', uploadFile);    // 作成したFormDataオブジェクトへ'file'キーとファイル実体をセットにして追加 -> 'file'はforms.py参照
    fetch(textarea.dataset.url, {           // textareaのデータ属性url指定していろいろ取得する　fetchはXmlHttpRequestの代替
        method: 'POST',                     // POSTメソッド
        body: formData,                     // このクラスで新規生成されたformdataオブジェクトを指定
        headers: {
            'X-CSRFToken': csrftoken,       // headerをcsrftoken?フォームのセキュリティ上必須らしい
        },
    // fetchで取得したresponseオブジェクトをprimisに渡して処理させる
    }).then(response => {                   
        return response.json();     // responseオブジェクト内のjsonを取得して返す。returnで結果を次の.Thenに渡す。

    // returnで指定されたresponse.josn()をresponseとして使用する
    }).then(response => {
        //ファイルの拡張子を抽出
        //responseオブジェクト内のurlをドット区切りの配列に変換し最後尾を削除後小文字にしたものを格納＝ファイル拡張子
        // responseオブジェクト内のurl = ファイル名の後ろにパス？＋拡張子。
        //const extension = response.url.split('.').pop().toLowerCase(); 

        // 抽出した拡張子に応じて処理分岐
        // 画像ならimg要素に、そうでなければa要素に
        //if (['png', 'jpg', 'gif', 'jpeg', 'bmp'].includes(extension)) { // 'png'～'bmp'の配列内要素がextentionに存在しているか？
        extentionavailability = extensioncheck_txt(response.url)    //拡張子のチェックし結果を格納

        if (extentionavailability) {        //拡張子が有効であればファイル名取得
            //html = `<a href="${response.url}"><img src="${response.url}"></a>`;
            filetext = uploadFile.name + '/ Extention OK/'
        } else {
            //html= `<a href="${response.url}">${response.url}</a>`;
            //html = uploadFile.name      // uploadしたfilename
            filetext = uploadFile.name + '/ Extention Bad/'
        }
           
        insertText(textarea, filetext);     // textareaに文字列を挿入 insertText関数呼び出し

        return extentionavailability;       //次の.Thenに渡す

    }).then(extentionavailability => {
        if(extentionavailability) {      //extentionavailabilityがtrueの時のみ処理実行　=拡張子が有効
            
            _a = readfileshow(uploadFile, textarea);
            
            
        }
    }).catch(error => {     // 処理拒絶（通信不良など）の場合。erroe object渡す
        console.log(error);     //デバッガのコンソールにerror内容。
    });
};

//テンプレートにドラッグアンドドロップのイベントに処理を追加する処理
document.addEventListener('DOMContentLoaded', e => {
    for (const textarea of document.querySelectorAll('textarea.uploadable')) {  //fomrs.py内の「widgets=」で指定した全てのテキストエリアが対象に
        textarea.addEventListener('dragover', e => {    //対象へドラッグした時のイベント
            e.preventDefault();     // 動作キャンセル時のイベント　（）内に処理関数入れる
        });

        textarea.addEventListener('drop', e => {        //対象にドロップした時のイベント
            e.preventDefault();     // 動作キャンセル時のイベント　（）内に処理関数入れる
            upload(e.dataTransfer.files[0], textarea);      //同じjsファイル内の「upload」を呼び出す。1番目の引数はドロップしたファイル1個。2番目が対象テキストエリア
        });
    }
});


