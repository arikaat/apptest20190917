//外部javascript
//template上にドラッグアンドドロップに連動したイベントを追加
//ファイルをアップロードする
//読み込んでストリームを渡すのみ。
//処理後取得したファイルデータは削除する。

//本クラスの名前空間
var DjkApp_Upload_Const = DjkApp_Upload_Const || {
    FIle_Upload:{},
    insert_Text:{},
    extensioncheck_txt:{},
    readfileshow:{}
};


// dropされたfileをreadするobject
DjkApp_Upload_Const.readfileshow = {
    create: function(_readfile, _setobj){
        //object生成と参照
        let obj     = Object.create(this.prototype);
        
        //property set
        obj.setobj  = _setobj;
        obj.readfile = _readfile;

        return obj;		// 作成したオブジェクトを返す。
    },

    // プロトタイプ宣言。 method は全てここに
	prototype:{	
		showobj_and_getdata: function(){
            new Promise((resolve, reject) => {      //resolve=次の.thenに渡すもの。 reject＝まだよくわからない。20190902
                const fileReader = new FileReader() ;   //filereader objectを生成
                fileReader.onload = function () {       //onloadイベント処理。読み込み成功後がトリガ。
                    console.log( this.result ) ;        //ブラウザのconsoleに出力
                    resolve(this.result);               //resolveに読み込み結果を格納。関数でもいいらしい。
                };
                fileReader.readAsText( this.readfile ) ;    //読み込み処理。

            }).then((result) => {       //上記promise処理後に実行される処理。
                //ファイルの中身をwidgetsへ出力する処理
                let _result_textarea = DjkApp_Upload_Const.insert_Text.create(this.setobj, '\n' + result);
                _result_textarea.insert();
                
                return result;  //ファイル読み取り結果を返す。
            });
        }
    }
};

// ドロップされたfileの拡張子をcheckする .txt .csv のみ
//responseurl = ドロップされたファイルのurl
DjkApp_Upload_Const.extensioncheck_txt = {
    create: function(_responseurl){
        //object生成と参照
        let obj     = Object.create(this.prototype);

        //property set
        obj.responseurl = _responseurl;

        return obj;		// 作成したobjectを返す。
    },

    // プロトタイプ宣言。 method は全てここに
	prototype:{	
        to_check: function(){
            let _extension = this.responseurl.split('.').pop().toLowerCase(); 
            if (['txt', 'csv'].includes(_extension)) { // 'txt'～'csv'の配列内要素がextentionに存在しているか？
                return true;
            } else {
                return false;
            }
        }
    }
};

// ドロップされたfileの拡張子をcheckする .txt .csv のみ
//responseurl = ドロップされたファイルのurl
DjkApp_Upload_Const.insert_Text = {
    create: function (_obj, _text) {
        //object生成と参照
        let obj     = Object.create(this.prototype);

        //property set
        obj.obj_insert  = _obj;
        obj.txt_insert  = _text;

        return obj;		// 作成したobjectを返す。
    },

    // プロトタイプ宣言。 method は全てここに
    prototype:{
        insert: function(){
            const cursorPos      = this.obj_insert.selectionStart;              //textarea内のカーソル位置
            const last     = this.obj_insert.value.length;                      //文字列最終位置
            const before   = this.obj_insert.value.substr(0, cursorPos);        //挿入前の文字列
            const after    = this.obj_insert.value.substr(cursorPos, last);     //挿入後の文字列
            this.obj_insert.value = before + this.txt_insert + after;           //文字列をtextareaへ挿入
        }
    }
};


// ドロップされたファイルの内容をアップロードする処理。
//　1番目の引数はファイル単体
//　2番目はアップロード結果を反映させるテキストエリアの参照。
DjkApp_Upload_Const.FIle_Upload = {
    create: function (_uploadFile, _showobj) {
        //object生成と参照
        let obj     = Object.create(this.prototype);

        //property set
        obj.obj_file    = _uploadFile;
        obj.obj_insert  = _showobj;
        obj.txt_result  = '';

        return obj;		// 作成したobjectを返す。
    },

    // プロトタイプ宣言。 method は全てここに
    prototype:{
        uploading: function(){
            const formData = new FormData();        // 新しいFormDataオブジェクトを作成。XmlHttoRequest関連
            formData.append('file', this.obj_file);     // 作成したFormDataオブジェクトへ'file'キーとファイル実体をセットにして追加 -> 'file'はforms.py参照
            
            fetch(this.obj_insert.dataset.url, {        // textareaのデータ属性url指定していろいろ取得する　fetchはXmlHttpRequestの代替
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

                //拡張子チェックオブジェクト生成と判定結果取得  
                let obj_extcheck       = DjkApp_Upload_Const.extensioncheck_txt.create(response.url);
                let bol_checkresult    = obj_extcheck.to_check();
        
                if (bol_checkresult) {        //拡張子が有効であればファイル名取得
                    //html = `<a href="${response.url}"><img src="${response.url}"></a>`;
                    _filetext = this.obj_file.name + '/ Extention OK/';
                } else {
                    //html= `<a href="${response.url}">${response.url}</a>`;
                    //html = uploadFile.name      // uploadしたfilename
                    _filetext = this.obj_file.name + '/ Extention Bad/';
                }

                //ファイル読み取り結果の表示
                let _result_textarea = DjkApp_Upload_Const.insert_Text.create(this.obj_insert, _filetext);
                _result_textarea.insert();

                return bol_checkresult;       //次の.Thenに渡す

            //fileread and getdata
            }).then(bol_checkresult => {
                if(bol_checkresult) {      //extentionavailabilityがtrueの時のみ処理実行　=拡張子が有効
                    let _a = DjkApp_Upload_Const.readfileshow.create(this.obj_file, this.obj_insert);
                    return _a.showobj_and_getdata();
                }
            }).catch(error => {     // 処理拒絶（通信不良など）の場合。erroe object渡す
                console.log(error);     //デバッガのコンソールにerror内容。
            });
        }
    }
    //prototype end
};

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
        let obj_extcheck       = DjkApp_Upload_Const.extensioncheck_txt.create(response.url);
        let bol_checkresult    = obj_extcheck.to_check();
        
        if (bol_checkresult) {        //拡張子が有効であればファイル名取得
            //html = `<a href="${response.url}"><img src="${response.url}"></a>`;
            filetext = uploadFile.name + '/ Extention OK/'
        } else {
            //html= `<a href="${response.url}">${response.url}</a>`;
            //html = uploadFile.name      // uploadしたfilename
            filetext = uploadFile.name + '/ Extention Bad/'
        }
        
        let _result_textarea = DjkApp_Upload_Const.insert_Text.create(textarea, filetext);
        _result_textarea.insert();

        //insertText(textarea, filetext);     // textareaに文字列を挿入 insertText関数呼び出し

        return bol_checkresult;       //次の.Thenに渡す

    }).then(bol_checkresult => {
        if(bol_checkresult) {      //extentionavailabilityがtrueの時のみ処理実行　=拡張子が有効
            
            let _a = DjkApp_Upload_Const.readfileshow.create(uploadFile, textarea);
            let _b = _a.showobj_and_getdata();
            
        }
    }).catch(error => {     // 処理拒絶（通信不良など）の場合。erroe object渡す
        console.log(error);     //デバッガのコンソールにerror内容。
    });
};

//------------------------------------------------------------------------------------------
// スクリプトをDOM要素（画像は対象外）読み込み完了後に実行させる
// 自動で処理したい場合に一番最初の処理をここに書く。
//------------------------------------------------------------------------------------------
//document.addEventListener('DOMContentLoaded', function() {  //昔はこっちの書き方。
document.addEventListener('DOMContentLoaded', e => {
    for (const textarea of document.querySelectorAll('textarea.uploadable')) {  //fomrs.py内の「widgets=」で指定した全てのテキストエリアが対象に
        textarea.addEventListener('dragover', e => {    //対象へドラッグした時のイベント
            e.preventDefault();     // 動作キャンセル時のイベント　（）内に処理関数入れる
        });

        textarea.addEventListener('drop', e => {        //対象にドロップした時のイベント
            e.preventDefault();     // 動作キャンセル時のイベント　（）内に処理関数入れる
            //upload(e.dataTransfer.files[0], textarea);      //同じjsファイル内の「upload」を呼び出す。1番目の引数はドロップしたファイル1個。2番目が対象テキストエリア
        
            //イベントの挿入。
            const _upload = DjkApp_Upload_Const.FIle_Upload.create(e.dataTransfer.files[0], textarea);
            return _upload.uploading();
        });
    }

});


