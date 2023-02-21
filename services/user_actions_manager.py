'''Define APIs relate to actions defined in user menu. API will contact with model, check user's information and return an array of line reply messages.'''
import models, smtplib, random, boto3
from . import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, PostbackAction

text_dict = {
    #Edit
    "Edit all": "將依序設定以下資料：\n1.性別\n2.希望配對性別\n3.line id\n4.出生年份\n5.學校信箱",
    "Begin modify": "請透過下列按鈕選擇希望更改的資料",
    "Null profile": "尚未設定{profile_type}",
    "Present profile": "目前的{profile_type}為 {profile}",
    "Update successfully": "已成功更改為 {value}",
    "Edit profile": "請在底下輸入您的{profile_type}",
    "My profile": "line ID: {lineID}\n性別: {gender}\n希望配對性別: {expect_gender}\n出生年份{year}\n信箱{email}",
    "Error message": "發生未知錯誤，請再試一次或是聯繫服務人員",

    #lineID
    "lineID too long": "您的line id過長，請聯繫服務人員",
    "lineID too long, try again": "您的line id過長，請再試一次",

    #gender
    "Choose gender": "請選擇以下性別",

    #birth_year
    "Not year": "請輸入數字作為年份\n請重新輸入一次",
    "Year out of range": "請輸入介於1983~2005之西元年\n請重新輸入一次",

    #email
    "Repeat email": "此信箱已經被註冊過了",
    "Improper email": "此信箱不是台大學校信箱",
    "Verifying email title": "換書交友活動 認證信",
    "Verifying email content": "您的驗證碼為{code}。請勿回覆此訊息。",
    "Input verifying code": "驗證碼已發送至{email}，請輸入驗證碼",
    "Wrong verifying code": "驗證碼錯誤，請重新輸入一次",

    #teaching
    "Teaching": "歡迎使用我們的交友服務！\n我們團隊希望能提供不同於交友軟體的速食戀愛體驗，透過不定期舉辦的活動讓您找到滿意的另一半！\n\n請先使用下方的功能列的「設定全部資料」功能輸入基本資料，若有輸入錯誤可透過「修改資料」修改個別項目。全部填妥後才能參加我們的活動喔\n在活動中找到感興趣的人送出配對邀請，如果對方接受的話即可獲得對方的line ID\n\n快點開始配對吧~\n\n*註：操作僅能於手機中完成。個人資訊僅用於活動中",
    "User contract": "使用者條款\n\n當您開始使用 台大有沒友（以下簡稱「本服務」）時，代表您已閱讀、了解並同意本使用條款（以下簡稱「條款」）及隱私權政策。若您不同意本條款或隱私權政策中的內容，請勿使用本服務。\n台大有沒友 可能隨時修改本條款及隱私權政策，修改後立即生效，不另行通知，請用戶於使用本服務時，隨時參閱最新版本的使用條款。若您於使用者條款與隱私權政策變更或修改後繼續使用本平台或相關服務，代表您同意遵守所有變更或修改後之內容。\n\n隱私權\n\n本服務尊重用戶的隱私權。本服務將會以安全的方式管理自用戶處蒐集的資料，並對安全管理採取嚴格的措施。本服務依據您授予的權限，收集您使用我們服務的電腦、手機相關的資訊，包含但不限定於作業系統、硬體版本及裝置識別碼等屬性。另請謹慎保護您自己的隱私資料，請勿輕易將信用卡及私密個人資料提供與平台及其他用戶。\n\n帳戶使用規範\n\n您必須使用自己的個人資訊註冊，且不得由他人代為註冊。\n您只能擁有一個 台大有沒友 帳戶，不得重複註冊多個帳戶。\n您不得將自己的帳戶販售、轉讓給其他人使用、或與他人共用。\n使用本服務時，請您能確實遵守適當法律和道德規範。\n當您使用本平台或其相關服務時，都必須符合所有適用於您的法規。\n您同意不會做出任何可能危害本平台安全的行為、或令其他人無法登錄使用本平台、或對本平台及其內容造成損害。\n您同意當發現您的使用者帳號或密碼被非法盜用或發現本站網管安全漏洞時會立刻通知我們。\n非經本平台同意，您不會任意增加、刪減或修改本平台或其他相關服務之內容。\n您同意不會使用本平台或其他服務從事會危害本平台權益或第三方權益的行為。\n我們提供本平台與相關服務僅提供個別使用者作個人使用，不得被使用於營利相關的商業用途上。\n\n用戶與用戶間的互動\n\n我們不會審查使用者的身份或背景，也不會檢查該使用者在本平台個人檔案中所陳述資料的真實性。您有責任維持並更新您所有的個人資料，確保其為正確、最新及完整性。\n我們保留審核您所提供的個人文字、照片等資料的權利，若您提供任何不實、錯誤、不完整、不適當的資料，我們有權暫停或是終止您的帳號，並且拒絕您使用本平台服務之全部或一部份。\n我們有權利監視，但是沒有義務處理您與其他使用者的個人糾紛。您與其他使用者的互動或糾紛由您自行負所有法律上之責任。\n您理解網路交友具有某些程度上的風險。透過網路您所結交的網友有可能是未成年人或使用虛假身份或有犯罪企圖人士。若您發現有前開情形時，歡迎向我們反應，我們會採取適當措施，以維護平台之良好使用環境。\n您同意當您與其他使用者接觸時，不論是在本網站或透過其他通訊軟體、平台、電話、或直接碰面的情況，您會以適當措施保護自己的個人安全與個人資料的隱私。不論在任何情況下都不要把您的地址、電話、私密照片、銀行帳號或信用卡號碼等個人私密資料透露給其他使用者。\n如您利用本平台提供之服務進行詐欺或其他不法之情事，您需要為自身行為負責。\n\n禁止行為與承諾\n\n本服務盡力維護用戶安全，要維持本服務及用戶安全，需要用戶的協助，包括以下承諾。\n1.	您不會以任何方式利用本服務傳送給使用者垃圾電郵，直銷，連鎖信或其他商業廣告信。\n2.	您不會抓取、蒐集、索引、探勘本服務的內容與使用者資料，或以其他方式在未經我們事先許可，使用自動化方式登入 本服務（如機器人、網路蜘蛛或網路爬蟲等軟體）。\n3.	您不會進行任何會關閉、超載或損害 台大有沒友 正常運作和外觀的事情，如拒絕服務攻擊或干擾呈現頁面或其他 台大有沒友 功能等。\n4.	您不會在本服務向其它使用者廣告、推銷商品或服務，或從事非法多層次傳銷，如金字塔式傳銷。\n5.	您不會刊登、傳送或散布軟體病毒或類似惡意的電腦程式語言、檔案或程式。\n6.	您不會霸凌、恐嚇、騷擾，追蹤或傷害他人。\n7.	您不會發表或傳送給其他使用者任何不適當的內容，包含但不限於鼓吹仇恨、威脅、色情、煽動暴力或帶有裸露或血腥暴力傾向。\n8.	您不會使用本服務進行任何非法、誤導、惡意或歧視的行為。\n9.	您不會違反任何法律或法規，包括信用卡詐騙或銀行帳戶詐騙；\n10.	您不會協助或鼓勵任何違反本協議或政策的行為。\n11.	您不會刊登，傳送或複製任何受著作權、商標保護的內容或其他相關資訊。\n12.	您不會修改、改寫、翻譯、銷售或用返向工程方式拆開或破解本平台與其相關服務的任何一部份內容、技術或軟體。\n\n若您違反上述承諾及禁止事項，或經用戶據報有違反包含但不限於上述之行為時，我們有權禁止您的使用，如因而導致您有任何的損失，將由您自行負擔，本平台不負責任何因使用者帳號被終止而產生的損失。\n\n用戶責任與免責聲明\n\n台大有沒友 以本服務現況所具備之條件提供服務及其內容。我們不會答應或保證用本平台或相關服務會獲得您所期望的效果。您因為取信本服務，或是其他使用者傳送給您的任何資訊，所造成任何相關傷害或間接損失，我們將不會為此負任何法律上的責任。\n本服務可能會出現延遲、中斷、故障或是遭受網路駭客等外力入侵、其他用戶對您的不當舉止等，造成您使用上不便、連線中斷、資料喪失，或其他經濟上、身心上損失等情形。您於使用本服務時宜自行採取防護措施，本服務對於您因使用本服務而造成的損害，不負任何法律上的責任。\n\n其他條款\n\n本服務鄭重提醒用戶注意本協議禁止行為與用戶責任及免責聲明，請用戶仔細閱讀，自主考慮風險。\n未成年人應在法定監護人的陪同下閱讀本協議。本服務保留本協議一切解釋和修改權利。",
    "How to edit lineID": "請透過文字輸入line id送出\n若line id超過120字，請聯繫服務人員",
    "How to edit gender": "請透過下方按鈕選擇\"男\", \"女\", \"非二元\"為自己的性別\n請勿透過文字輸入\n配對時只會配對到性別與希望配對性別剛好對應的參加者喔",
    "How to edit expect_gender": "請透過下方按鈕選擇\"男\", \"女\", \"非二元\"為希望配對到的性別\n請勿透過文字輸入\n配對時只會配對到性別與希望配對性別剛好對應的參加者喔",
    "How to edit birth_year": "請透過文字輸入介於1983~2005之西元年並送出",
    "How to edit email": "1.透過文字輸入email並送出\n2.到學校信箱取得驗證碼\n3.透過文字輸入驗證碼並送出\n驗證碼若輸入錯誤請直接再試一次，若想退出請按\"取消\"",

    #other
    "Welcome": "歡迎使用本服務～\n\n若想參加活動，請先使用下方功能按鈕更新資料並驗證",
    "Contact info": "Email: letsmeettoday.service@gmail.com\nFacebook: https://www.facebook.com/profile.php?id=100003508569457&mibextid=LQQJ4d",
    "Cancel action": "已取消動作",
    "Repeat": "請再試一次"

}

department_dict = {
    "0020":"體育室",
    "0030":"軍訓室",
    "0040":"外語教學暨資源中心",
    "0050":"學務處課外活動組",
    "1000":"文學院",
    "1010":"中國文學系",
    "1011":"中國文學系國際學生學士班",
    "1020":"外國語文學系",
    "1030":"歷史學系",
    "1040":"哲學系",
    "1050":"人類學系",
    "1060":"圖書資訊學系",
    "1070":"日本語文學系",
    "1080":"應用英語學系",
    "1090":"戲劇學系",
    "1210":"中國文學研究所",
    "1220":"外國語文學研究所",
    "1230":"歷史學研究所",
    "1240":"哲學研究所",
    "1250":"人類學研究所",
    "1260":"圖書資訊學研究所",
    "1270":"日本語文學研究所",
    "1290":"戲劇學研究所",
    "1410":"藝術史研究所",
    "1420":"語言學研究所",
    "1440":"音樂學研究所",
    "1450":"臺灣文學研究所",
    "1460":"華語教學碩士學位學程",
    "1470":"翻譯碩士學位學程",
    "2000":"理學院",
    "2010":"數學系",
    "2020":"物理學系",
    "2030":"化學系",
    "2040":"地質科學系",
    "2050":"動物學系",
    "2051":"動物生物組",
    "2052":"漁業生物組",
    "2060":"植物學系",
    "2070":"心理學系",
    "2080":"地理環境資源學系",
    "2090":"大氣科學系",
    "2210":"數學研究所",
    "2220":"物理學研究所",
    "2230":"化學研究所",
    "2231":"化學所化學組",
    "2232":"化學所化學生物學組",
    "2240":"地質科學研究所",
    "2241":"地質組",
    "2242":"應用地質組",
    "2250":"動物學研究所",
    "2260":"植物學研究所",
    "2270":"心理學研究所",
    "2271":"一般心理學組",
    "2272":"臨床心理學組",
    "2280":"地理環境資源學研究所",
    "2290":"大氣科學研究所",
    "2410":"海洋研究所",
    "2411":"海洋物理組",
    "2412":"海洋生物及漁業組",
    "2413":"海洋地質及地球物理",
    "2414":"海洋化學組",
    "2440":"天文物理研究所",
    "2450":"應用物理學研究所",
    "2460":"應用數學科學研究所",
    "2470":"氣候變遷與永續發展國際學位學程",
    "2490":"地球系統科學國際研究生博士學位學程",
    "2500":"統計與數據科學研究所",
    "3000":"社會科學院",
    "3020":"政治學系",
    "3021":"政治理論組",
    "3022":"國際關係組",
    "3023":"公共行政組",
    "3030":"經濟學系",
    "3050":"社會學系",
    "3051":"社會學組",
    "3052":"社會工作組",
    "3100":"社會工作學系",
    "3220":"政治學研究所",
    "3230":"經濟學研究所",
    "3250":"社會學研究所",
    "3300":"社會工作學研究所",
    "3410":"國家發展研究所",
    "3420":"新聞研究所",
    "3430":"公共事務研究所",
    "4000":"醫學院",
    "4010":"醫學系",
    "4020":"牙醫學系",
    "4030":"藥學系",
    "4031":"藥學系六年制",
    "4040":"醫學檢驗暨生物技術學系",
    "4060":"護理學系",
    "4080":"物理治療學系",
    "4081":"物治系六年制",
    "4090":"職能治療學系",
    "4120":"學士後護理學系",
    "4200":"醫學院暨公共衛生學院共同課程",
    "4210":"臨床醫學研究所",
    "4213":"臨床醫學研究所 臨床醫學研究組",
    "4214":"臨床醫學研究所 臨床試驗組",
    "4220":"臨床牙醫學研究所",
    "4230":"藥學研究所",
    "4231":"藥學系博士班藥物科技組",
    "4232":"藥學系博士班分子醫藥組",
    "4233":"藥學系博士班產學研發組",
    "4240":"醫學檢驗暨生物技術學研究所",
    "4260":"護理學研究所",
    "4280":"物理治療學研究所",
    "4290":"職能治療學研究所",
    "4410":"生理學研究所",
    "4420":"生物化學暨分子生物學研究所",
    "4430":"藥理學研究所",
    "4440":"病理學研究所",
    "4450":"微生物學研究所",
    "4451":"微生物及免疫學組",
    "4452":"寄生蟲組",
    "4453":"微生物學研究所熱帶醫學暨寄生蟲學組",
    "4460":"解剖學暨細胞生物學研究所",
    "4470":"毒理學研究所",
    "4480":"分子醫學研究所",
    "4490":"免疫學研究所",
    "4500":"口腔生物科學研究所",
    "4510":"臨床藥學研究所",
    "4520":"法醫學研究所",
    "4530":"腫瘤醫學研究所",
    "4540":"腦與心智科學研究所",
    "4550":"基因體暨蛋白體醫學研究所",
    "4560":"轉譯醫學博士學位學程",
    "4570":"醫學教育暨生醫倫理研究所",
    "4580":"醫療器材與醫學影像研究所",
    "4590":"國際三校農業生技與健康醫療碩士學位學程",
    "5000":"工學院",
    "5010":"土木工程學系",
    "5020":"機械工程學系",
    "5040":"化學工程學系",
    "5050":"工程科學及海洋工程學系",
    "5070":"材料科學與工程學系",
    "5080":"醫學工程學系",
    "5090":"智慧工程科技全英語學士學位學程",
    "5210":"土木工程學研究所",
    "5211":"大地工程組",
    "5212":"結構工程組",
    "5213":"水利工程組",
    "5215":"交通工程組",
    "5216":"電腦輔助工程組",
    "5217":"營建工程與管理組",
    "5218":"測量及空間資訊組",
    "5220":"機械工程學研究所",
    "5221":"流體力學組",
    "5223":"熱學組",
    "5224":"航空工程組",
    "5225":"固體力學組",
    "5226":"設計組",
    "5227":"製造組",
    "5228":"系統控制組",
    "5240":"化學工程學研究所",
    "5250":"工程科學及海洋工程學研究所",
    "5270":"材料科學與工程學研究所",
    "527A":"材料科學與工程學研究所國際應用材料工程碩",
    "5280":"醫學工程學研究所",
    "5410":"環境工程學研究所",
    "5430":"應用力學研究所",
    "5440":"建築與城鄉研究所",
    "5460":"工業工程學研究所",
    "5480":"醫學工程學研究所",
    "5490":"高分子科學與工程學研究所",
    "5500":"綠色永續材料與精密元件博士學位學程",
    "5510":"分子科學與技術國際研究生博士學位學程",
    "5520":"永續化學科技國際研究生博士學位學程",
    "6000":"生物資源暨農學院",
    "6010":"農藝學系",
    "6020":"生物環境系統工程學系",
    "6030":"農業化學系",
    "6031":"土壤肥料組",
    "6032":"農產製造組",
    "6040":"植物病蟲害學系",
    "6050":"森林環境暨資源學系",
    "6051":"育林組",
    "6052":"資源管理組",
    "6053":"森林工業組",
    "6054":"森林資源保育組",
    "6060":"動物科學技術學系",
    "6070":"農業經濟學系",
    "6080":"園藝暨景觀學系",
    "6090":"獸醫學系",
    "6100":"生物產業傳播暨發展學系",
    "6101":"推廣教育組",
    "6102":"鄉村社會組",
    "6110":"生物機電工程學系",
    "6120":"昆蟲學系",
    "6130":"植物病理與微生物學系",
    "6210":"農藝學研究所",
    "6211":"作物科學組",
    "6212":"生物統計學組",
    "6220":"生物環境系統工程學研究所",
    "6230":"農業化學研究所",
    "6234":"土壤環境與植物營養組",
    "6235":"生物工業化學組",
    "6236":"生物化學組",
    "6237":"營養科學組",
    "6238":"微生物學組",
    "6250":"森林環境暨資源學研究所",
    "6260":"動物科學技術學研究所",
    "6270":"農業經濟學研究所",
    "6280":"園藝暨景觀學研究所",
    "6281":"園藝作物組",
    "6282":"園產品處理及利用組",
    "6283":"景觀暨休憩組",
    "6290":"獸醫學研究所",
    "6300":"生物產業傳播暨發展學研究所",
    "6310":"生物產業機電工程學研究所",
    "6320":"昆蟲學研究所",
    "6330":"植物病理與微生物學研究所",
    "6410":"食品科技研究所",
    "6420":"生物科技研究所",
    "6430":"臨床動物醫學研究所",
    "6440":"分子暨比較病理生物學研究所",
    "6450":"植物醫學碩士學位學程",
    "7000":"管理學院",
    "7010":"工商管理學系",
    "7011":"企業管理組",
    "7012":"科技管理組",
    "7013":"工商管理系企業管理組英文專班",
    "7020":"會計學系",
    "7030":"財務金融學系",
    "7040":"國際企業學系",
    "7050":"資訊管理學系",
    "7060":"企業管理學系",
    "7220":"會計學研究所",
    "7230":"財務金融學研究所",
    "7240":"國際企業學研究所",
    "7250":"資訊管理學研究所",
    "7400":"高階管理碩士專班(EMBA)",
    "7410":"商學研究所",
    "7420":"管院知識管理組",
    "7430":"管理學院高階公共管理組",
    "7440":"管理學院會計與管理決策組",
    "7450":"管理學院財務金融組",
    "7460":"管理學院國際企業管理組",
    "7470":"管理學院資訊管理組",
    "7480":"管理學院商學組",
    "7490":"管理學院企業管理碩士專班(GMBA)",
    "7500":"臺大-復旦EMBA",
    "7510":"創業創新管理碩士在職專班",
    "8000":"公共衛生學院",
    "8010":"公共衛生學系",
    "8410":"職業醫學與工業衛生研究所",
    "8420":"流行病學研究所",
    "8430":"醫療機構管理研究所",
    "8440":"環境衛生研究所",
    "8450":"衛生政策與管理研究所",
    "8470":"公共衛生碩士學位學程",
    "8480":"健康政策與管理研究所",
    "8481":"健康促進組",
    "8482":"健康服務與產業組",
    "848A":"健管所高階經營碩士在職專班",
    "8490":"流行病學與預防醫學研究所",
    "8491":"流預所流行病學組",
    "8492":"流預所生物醫學統計組",
    "8493":"流預所預防醫學組",
    "8500":"健康行為與社區科學研究所",
    "8510":"食品安全與健康研究所",
    "8520":"環境與職業健康科學研究所",
    "8530":"全球衛生碩士學位學程",
    "8540":"全球衛生博士學位學程",
    "9000":"電機資訊學院",
    "9010":"電機工程學系",
    "9020":"資訊工程學系",
    "9210":"電機工程學研究所",
    "9220":"資訊工程學研究所",
    "9410":"光電工程學研究所",
    "9420":"電信工程學研究所",
    "9430":"電子工程學研究所",
    "9440":"資訊網路與多媒體研究所",
    "9450":"生醫電子與資訊學研究所",
    "9460":"資料科學學位學程",
    "9470":"生物資訊學國際研究生學位學程",
    "9480":"資料科學博士學位學程",
    "9490":"智慧聯網國際研究生博士學位學程",
    "A000":"法律學院",
    "A010":"法律學系",
    "A011":"法學組",
    "A012":"司法組",
    "A013":"財法組",
    "A210":"法律研究所",
    "A408":"教學發展中心",
    "A410":"科際整合法律學研究所",
    "B000":"生命科學院",
    "B010":"生命科學系",
    "B020":"生化科技學系",
    "B210":"生命科學所",
    "B220":"生化科技研究所",
    "B420":"植物科學研究所",
    "B430":"分子與細胞生物學研究所",
    "B440":"生態學與演化生物學研究所",
    "B450":"漁業科學研究所",
    "B460":"生化科學研究所",
    "B470":"微生物與生化學研究所",
    "B471":"生物工業組",
    "B472":"生物化學組",
    "B473":"營養科學組",
    "B474":"微生物學組",
    "B480":"基因體與系統生物學學位學程",
    "B490":"跨領域神經科學國際研究生博士學位學程",
    "E000":"進修推廣學院",
    "E410":"事業經營碩士在職學位學程",
    "E420":"事業經營法務碩士在職學位學程",
    "E430":"生物科技管理碩士在職學位學程",
    "G010":"台北教育大學",
    "H000":"共同教育中心",
    "H010":"通識教育組",
    "H020":"共同教育組",
    "H040":"國際體育運動事務學士學位學程",
    "H410":"統計碩士學位學程",
    "H420":"運動設施與健康管理碩士學位學程",
    "H430":"全球農業科技與基因體科學碩士學位學程",
    "H440":"生物多樣性國際碩士學位學程",
    "H450":"智慧醫療與健康資訊碩士學位學程",
    "I000":"國際學院",
    "J000":"產業研發碩士專班",
    "J100":"電機電信電子產業研發碩士專班",
    "J110":"資訊產業研發碩士專班",
    "K000":"重點科技研究學院與三校聯盟",
    "K010":"國立臺灣師範大學",
    "K020":"國立臺灣科技大學",
    "K030":"國立臺北教育大學",
    "K410":"積體電路設計與自動化碩士學位學程",
    "K420":"積體電路設計與自動化博士學位學程",
    "K430":"元件材料與異質整合碩士學位學程",
    "K440":"元件材料與異質整合博士學位學程",
    "K450":"奈米工程與科學碩士學位學程",
    "K460":"奈米工程與科學博士學位學程",
    "Q010":"寫作教學中心",
    "Q020":"生命教育研發育成中心",
    "V410":"國家理論科學研究中心",
    "Z000":"創新設計學院",
    "Z010":"創新領域學士學位學程",
}

cancel_quick_reply_button = QuickReplyButton(action = PostbackAction(label = "取消", display_text = "取消動作",data = "action=cancel&type=none"))
skip_setting_quick_reply_button = QuickReplyButton(action= PostbackAction(label = "跳過", display_text = "跳過", data = "action=edit_profile&type=skip"))

def add_new_user(userID: str):
    '''
    Insert userID into friends table and show welcome message. Ignoring whether the user has already followed or not.
    :param str userID: line userID
    :return an array of a single welcome text message.
    '''

    models.user.insert_user(userID)
    return [TextSendMessage(text = text_dict["Welcome"])]

def begin_modify(userID: str):
    '''
    Return a text message of teaching how to edit profile with quick replies to choose which type of profile to be changed.
    :param str userID: line user id
    '''

    #Get green and red image url
    s3 = boto3.client("s3", aws_access_key_id = config["aws_access_key_id"], aws_secret_access_key = config["aws_secret_access_key"])
    red_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "red.png"})
    green_url = s3.generate_presigned_url(ClientMethod = "get_object", ExpiresIn = 60, Params = {"Bucket": "linedatingapp", "Key": "green.png"})

    #Set NULL column with red_url, not Null with green_url
    profiles = models.user.get_user_profiles(userID, all = True)
    url_list = []
    for i in range(1, 6):
        if profiles[i] == None:
            url_list.append(red_url)
        else:
            url_list.append(green_url)

    quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "line id", data = "action=edit_profile&type=begin_lineID"), image_url = url_list[0]),
                    QuickReplyButton(action = PostbackAction(label = "性別", data = "action=edit_profile&type=begin_gender"), image_url = url_list[1]),
                    QuickReplyButton(action = PostbackAction(label = "希望配對性別", data = "action=edit_profile&type=begin_expect_gender"), image_url = url_list[2]),
                    QuickReplyButton(action = PostbackAction(label = "出生年份", data = "action=edit_profile&type=begin_birth_year"), image_url = url_list[3]),
                    QuickReplyButton(action = PostbackAction(label = "學校信箱", data = "action=edit_profile&type=begin_email"), image_url = url_list[4]),
                    cancel_quick_reply_button
                    ])
    return [TextSendMessage(text = text_dict["Begin modify"], quick_reply = quick_reply)]

def begin_edit_gender(userID: str, type: str):
    '''
    Show present gender setting and give quick replies to choose gender. Data in the PostbackAction: "action=edit_profile&type=choose_gender&field={type}&value=男"
    :param str userID: line userID
    :param str type: "begin_gender" or "begin_expect_gender"
    '''

    type = type[6:]
    quick_reply = QuickReply(
                items = [
                    QuickReplyButton(action = PostbackAction(label = "男", display_text = "男" ,data = f"action=edit_profile&type=choose_gender&field={type}&value=男")),
                    QuickReplyButton(action = PostbackAction(label = "女", display_text = "女",data = f"action=edit_profile&type=choose_gender&field={type}&value=女")),
                    QuickReplyButton(action = PostbackAction(label = "非二元", display_text = "非二元",data = f"action=edit_profile&type=choose_gender&field={type}&value=非二元")),
                    cancel_quick_reply_button
                ]
            )
    present_gender = models.user.get_user_profiles(userID, [type])[0]
    profile_dict = {"gender":"性別","expect_gender":"希望配對性別"}

    if present_gender == None:
        return [TextSendMessage(text = text_dict["Null profile"].format(profile_type = profile_dict[type])), TextSendMessage(text = text_dict["Choose gender"], quick_reply = quick_reply)]
    else:
        return [TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_dict[type], profile = present_gender)), TextSendMessage(text = text_dict["Choose gender"], quick_reply = quick_reply)]

def edit_user_profile(userID: str, field: str, value: str):
    '''
    Edit user profile(field). Return an message to tell the user to redo if exception happens.
    :param str userID: line userID
    :param str field: "lineID", "gender", "expect_gender", "birth_year" or "email"
    :param str value: value to be inserted
    '''

    if models.user.update_user_profile(userID, field, value):
        return [TextSendMessage(text = text_dict["Update successfully"].format(value = value))]
    else:
        return [TextSendMessage(text = text_dict["Error message"])]

def begin_edit_string_field(userID: str, type: str):
    '''
    Show present profile setting and teaching message.
    :param str userID: line userID
    :param str type: "begin_lineID", "begin_birth_year" or "begin_email"
    :param str warning_message: warning message about 
    '''
    
    type = type[6:]
    profile_dict = {"email":"學校信箱","birth_year":"出生年份","lineID":"line id"}
    value = models.user.get_user_profiles(userID, [type])[0]
    
    if type == "birth_year":
        warning_message = "\n請輸入介於1983~2005之西元年"
    elif type == "email":
        warning_message = "\n請使用台大信箱，需完成認證才算更改完畢"
    elif type == "lineID":
        warning_message = ""

    if value != None:
        return [TextSendMessage(text = text_dict["Present profile"].format(profile_type = profile_dict[type], profile = value)), TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_dict[type]) + warning_message, quick_reply = QuickReply(items = [cancel_quick_reply_button]))]
    else:
        return [TextSendMessage(text = text_dict["Null profile"].format(profile_type = profile_dict[type])), TextSendMessage(text = text_dict["Edit profile"].format(profile_type = profile_dict[type]) + warning_message, quick_reply = QuickReply(items = [cancel_quick_reply_button]))]

def teaching():
    '''
    Return teaching text message.
    '''

    quick_reply = QuickReply(
            items = [
                QuickReplyButton(action = PostbackAction(label = "用戶協議", display_text = "用戶協議" ,data = f"action=teaching&type=contract")),
                QuickReplyButton(action = PostbackAction(label = "如何編輯line ID", display_text = "如何編輯line ID" ,data = f"action=teaching&type=lineID")),
                QuickReplyButton(action = PostbackAction(label = "如何編輯（希望配對）性別", display_text = "如何編輯（希望配對）性別",data = f"action=teaching&type=gender")),
                QuickReplyButton(action = PostbackAction(label = "如何編輯出生年份", display_text = "如何編輯出生年份",data = f"action=teaching&type=birth_year")),
                QuickReplyButton(action = PostbackAction(label = "如何編輯學校信箱", display_text = "如何編輯學校信箱",data = f"action=teaching&type=email")),
                cancel_quick_reply_button
            ]
        )
    return [TextSendMessage(text = text_dict["Teaching"], quick_reply = quick_reply)]

def contact():
    '''
    Return contact text message.
    '''

    return [TextSendMessage(text = text_dict["Contact info"])]

def send_verifying_email(email: str):
    '''
    Send a verifying email if it is a ntu mail. If it is duplicated or isn't an ntu mail, return error message.
    :param str email: a ntu mail, must end with "ntu.edu.tw"
    :return a text message, bool indicate whether the email is legal, and verifying code
    '''

    if models.user.is_email_duplicated(email):
        return [TextSendMessage(text = text_dict["Repeat email"])], False, None

    #Check is it a ntu mail
    try:
        if email.split("@")[1] != "ntu.edu.tw":
            return [TextSendMessage(text = text_dict["Improper email"])], False, None
    except:
        return [TextSendMessage(text = text_dict["Improper email"])], False, None

    #Send verifying email
    content = MIMEMultipart()
    content["subject"] = text_dict["Verifying email title"]
    content["from"] = config["DOMAIN_MAIL_ACCOUNT"]
    content["to"] = email
    verifying_code = str(random.randint(100000, 999999))
    content.attach(MIMEText(text_dict["Verifying email content"].format(code = verifying_code)))
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config["DOMAIN_MAIL_ACCOUNT"], config["DOMAIN_MAIL_PASSWORD"])
            smtp.send_message(content)
        except Exception as e:
            print("Errpr message: ", e)
            return [TextSendMessage(text = text_dict["Fail to send email"])], False, None

    return [TextSendMessage(text = text_dict["Input verifying code"].format(email = email), quick_reply = QuickReply([cancel_quick_reply_button]))], True, verifying_code

def verify_email(userID: str, correct_code: str, entered_code: str, email: str):
    '''
    If entered_code == correct_code, update email into database, else return repeat message.
    :param str userID: line userID
    :param str correct_code: the correct verfy code
    :param str entered_code: the code entered by user
    :param str user: user's email
    :return a message and bool indicate whether entered_code is correct
    '''

    if correct_code != entered_code:
        return [TextSendMessage(text = text_dict["Wrong verifying code"], quick_reply = QuickReply(items = [cancel_quick_reply_button]))], False
    else:
        department = department_dict.get(str(email[3:7]).upper(), None)
        if department != None:
            models.user.update_user_profile(userID, "department", department)
        return edit_user_profile(userID, "email", email), True

def edit_birth_year(userID: str, birth_year: str):
    '''
    If birth_year is an int between 1983 and 2005, update user's profile, else return repeat message.
    :param str userID: line userID
    :param str birth_year: an int between 1983 and 2005
    :return a message and bool indicating whether the birth_year is valid
    '''

    try:
        birth_year = int(birth_year)
    except:
        return [TextSendMessage(text = text_dict["Not year"], quick_reply = QuickReply([cancel_quick_reply_button]))], False

    if birth_year <= 1983 or birth_year >= 2005:
        return [TextSendMessage(text = text_dict["Year out of range"], quick_reply = QuickReply([cancel_quick_reply_button]))], False
    else:
        return edit_user_profile(userID, "birth_year", str(birth_year)), True

def edit_lineID(userID: str, lineID: str):
    '''
    If len(lineID) > 120, return error message.
    :param str userID: line userID
    :param str lineID: line lineID
    '''

    if len(lineID) > 120:
        return [TextSendMessage(text = text_dict["lineID too long"])]
    return edit_user_profile(userID, "lineID", lineID)

def cancel():
    '''
    Return cancel text message.
    '''

    return TextSendMessage(text = text_dict["Cancel action"])

def contract():
    '''
    Return user contract line message.
    '''

    return TextSendMessage(text = text_dict["User contract"])

def teach(type: str):
    '''
    Return teaching text for specific field.
    :param str type: type in "lineID", "gender", "birth_year", "email"s
    '''

    key = "How to edit " + type
    try:
        result = [TextSendMessage(text = text_dict.get(key, None))]
        return result
    except:
        return [TextSendMessage(text = text_dict["Error message"])]

def begin_edit_all(userID: str):
    '''
    Show what fields have to be set and begin edit gender.
    :param str userID: line user id
    '''

    gender = models.user.get_user_profiles(userID, ["gender"])[0]
    quick_reply = QuickReply(
            items = [
                QuickReplyButton(action = PostbackAction(label = "男", display_text = "男" ,data = f"action=edit_profile&type=continuous_setting_gender&value=男")),
                QuickReplyButton(action = PostbackAction(label = "女", display_text = "女",data = f"action=edit_profile&type=continuous_setting_gender&value=女")),
                QuickReplyButton(action = PostbackAction(label = "非二元", display_text = "非二元",data = f"action=edit_profile&type=continuous_setting_gender&fvalue=非二元")),
                QuickReplyButton(action= PostbackAction(label = "跳過", display_text = "跳過", data = "action=edit_profile&type=continuous_setting_gender&fvalue=skip")), #a skip button to skip to continuous_setting_gender 
                cancel_quick_reply_button
            ]
        )
    if gender == None:
        return [TextSendMessage(text_dict["Edit all"]), TextSendMessage(text_dict["How to edit gender"], quick_reply = quick_reply)]
    else:
        return [TextSendMessage(text_dict["Edit all"]), TextSendMessage(text_dict["Present profile"].format(profile_type = "性別", profile = gender)), TextSendMessage(text_dict["How to edit gender"], quick_reply = quick_reply)]

def continuous_setting_gender(userID: str, gender: str):
    '''
    Update gender in the database.
    If gender is valid, will return a success message and a helping message of setting expect_gender.
    Return an array of messages and a bool indicated whether gender is valid.
    '''

    if gender not in ["男", "女", "非二元", "skip"]:
        return TextSendMessage(text_dict["Error message"]), False
    
    if gender != "skip":
        messages = edit_user_profile(userID, "gender", gender)
    else:
        messages = []
    expect_gender = models.user.get_user_profiles(userID, ["expect_gender"])[0]
    quick_reply = QuickReply(
            items = [
                QuickReplyButton(action = PostbackAction(label = "男", display_text = "男" ,data = f"action=edit_profile&type=continuous_setting_expect_gender&value=男")),
                QuickReplyButton(action = PostbackAction(label = "女", display_text = "女",data = f"action=edit_profile&type=continuous_setting_expect_gender&value=女")),
                QuickReplyButton(action = PostbackAction(label = "非二元", display_text = "非二元",data = f"action=edit_profile&type=continuous_setting_expect_gender&fvalue=非二元")),
                QuickReplyButton(action= PostbackAction(label = "跳過", display_text = "跳過", data = "action=edit_profile&type=continuous_setting_expect_gender&fvalue=skip")), #a skip button to skip to continuous_setting_expect_gender 
                cancel_quick_reply_button
            ]
        )
    if expect_gender != None:
        messages.append(TextSendMessage(text_dict["Present profile"].format(profile_type = "希望配對性別", profile = expect_gender)))
    messages.append(TextSendMessage(text_dict["How to edit expect_gender"], quick_reply = quick_reply))
    return messages, True

def continuous_setting_expect_gender(userID: str, expect_gender: str):
    '''
    Update expect_gender in the database.
    If gender is valid, will return a success message and a helping message of setting lineID.
    Return an array of messages and a bool indicated whether gender is valid.
    '''

    if expect_gender not in ["男", "女", "非二元", "skip"]:
        return TextSendMessage(text_dict["Error message"]), False
    
    if expect_gender != "skip":
        messages = edit_user_profile(userID, "expect_gender", expect_gender)
    else:
        messages = []

    lineID = models.user.get_user_profiles(userID, ["lineID"])[0]
    if lineID != None:
        messages.append(TextSendMessage(text_dict["Present profile"].format(profile_type = "line id", profile = lineID)))
    messages.append(TextSendMessage(text_dict["How to edit lineID"], quick_reply = QuickReply([skip_setting_quick_reply_button, cancel_quick_reply_button])))
    return messages, True

def continuous_setting_lineID(userID: str, lineID: str):
    '''
    Continuous_setting version of edit_lineID.
    If the id is valid, will return a success message and a helping message of setting birth_year.
    '''

    if len(lineID) > 120:
        return [TextSendMessage(text = text_dict["lineID too long, try again"], quick_reply = QuickReply([skip_setting_quick_reply_button, cancel_quick_reply_button]))], False
    if lineID == "skip":
        messages = []
    else:
        messages = edit_user_profile(userID, "lineID", lineID)
    birth_year = models.user.get_user_profiles(userID, ["birth_year"])[0]
    if birth_year != None:
        messages.append(TextSendMessage(text_dict["Present profile"].format(profile_type = "出生年份", profile = birth_year)))
    messages.append(TextSendMessage(text_dict["How to edit birth_year"], quick_reply = QuickReply([skip_setting_quick_reply_button, cancel_quick_reply_button])))
    return messages, True

def continuous_setting_birth_year(userID: str, birth_year: str):
    '''
    Continuous_setting version of edit_birth_year.
    If year is valid, will return a success message and a helping message of setting email.
    If year = skip, won't update birth_year.
    '''

    messages = []
    if birth_year != "skip":
        try:
            birth_year = int(birth_year)
        except:
            return [TextSendMessage(text = text_dict["Not year"], quick_reply = QuickReply([skip_setting_quick_reply_button, cancel_quick_reply_button]))], False

        if birth_year <= 1983 or birth_year >= 2005:
            return [TextSendMessage(text = text_dict["Year out of range"], quick_reply = QuickReply([skip_setting_quick_reply_button, cancel_quick_reply_button]))], False
        else:
            messages = edit_user_profile(userID, "birth_year", str(birth_year))
    messages.append(TextSendMessage(text_dict["How to edit email"], quick_reply = QuickReply([cancel_quick_reply_button])))
    return messages, True

def append_repeat_message(messages: list):
    '''
    Append a repeat message with cancel button to messages.
    :param list messages: a list of line SendMessage.
    '''

    messages.append(TextSendMessage(text_dict["Repeat"], quick_reply = QuickReply([cancel_quick_reply_button])))
    return messages