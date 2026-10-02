<h2>A.3 常用開發工具命令列參考</h2>

<p>A.3.1 gcc，GCC編譯器</p>

<p>-E：只進行預處理並把預處理結果輸出。</p>

<p>-c：只編譯不連結。</p>

<p>-o &lt;filename&gt;：指定輸出檔名。</p>

<p>-S：輸出編譯後的組合語言程式碼檔案。</p>

<p>-I：指定標頭檔路徑。</p>

<p>-e name：指定name為程式入口地址。</p>

<p>-ffreestanding：編譯獨立的程式，不會自動連結C執行庫、啟動檔案等。</p>

<p>-finline-functions,-fno-inline-functions：啟用/關閉行內函數。</p>

<p>-g：在編譯結果中加入除錯資訊，-ggdb就是加入GDB偵錯程式能夠識別的格式。</p>

<p>-L &lt;directory&gt;：指定連結時查詢路徑，多個路徑之間用冒號隔開。</p>

<p>-nostartfiles：不要連結啟動檔案，比如crtbegin.o、crtend.o。</p>

<p>-nostdlib：不要連結標準庫檔案，主要是C執行庫。</p>

<p>-O0：關閉所有最佳化選項。</p>

<p>-shared：產生共享物件檔案。</p>

<p>-static：使用靜態連結。</p>

<p>-Wall：對原始碼中的多數編譯警告進行啟用。</p>

<p>-fPIC：使用地址無關程式碼模式進行編譯。</p>

<p>-fPIE：使用地址無關程式碼模式編譯執行檔。</p>

<p>-XLinker &lt;option&gt;：把option傳遞給連結器。</p>

<p>-Wl &lt;option&gt;：把option傳遞給連結器，與上面的選項類似。</p>

<p>-fomit-frame-pointer：禁止使用EBP作為函式幀指標。</p>

<p>-fno-builtin：禁止GCC編譯器內建函式。</p>

<p>-fno-stack-protector：是指關閉堆疊保護功能。</p>

<p>-ffunction-sections：將每個函式編譯到獨立的程式碼段。</p>

<p>-fdata-sections：將全域性/靜態變數編譯到獨立的資料段。</p>

<p>A.3.2 ld，GNU連結器</p>

<p>-static：靜態連結。</p>

<p>-l&lt;libname&gt;：指定連結某個庫。</p>

<p>-e name：指定name為程式入口。</p>

<p>-r：合並目的檔，不進行最終連結。</p>

<p>-L &lt;directory&gt;：指定連結時查詢路徑，多個路徑之間用冒號隔開。</p>

<p>-M：將連結時的符號和地址輸出成一個對映檔案。</p>

<p>-o：指定輸出檔名。</p>

<p>-s：清除輸出檔案中的符號資訊。</p>

<p>-S：清除輸出檔案中的除錯資訊。</p>

<p>-T &lt;scriptfile&gt;：指定連結指令碼檔案。</p>

<p>-version-script &lt;file&gt;：指定符號版本指令碼檔案。</p>

<p>-soname &lt;name&gt;：指定輸出共用函式庫的SONAME。</p>

<p>-export-dynamic：將全域性符號全部匯出。</p>

<p>-verbose：連結時輸出詳細資訊。</p>

<p>–rpath &lt;path&gt;：指定連結時庫查詢路徑。</p>

<p>A.3.3 objdump，GNU目的檔執行檔檢視器</p>

<p>-a：列舉.a檔案中所有的目的檔。</p>

<p>-b bfdname：指定BFD名。</p>

<p>-C：對於C++符號名進行反修飾（Demangle）。</p>

<p>-g：顯示除錯資訊。</p>

<p>-d：對包含機器指令的段進行反組譯。</p>

<p>-D：對所有的段進行反組譯。</p>

<p>-f：顯示目的檔檔案頭。</p>

<p>-h：顯示段表。</p>

<p>-l：顯示行號資訊。</p>

<p>-p：顯示專有頭部資訊，具體內容取決於檔案格式。</p>

<p>-r：顯示重定位資訊。</p>

<p>-R：顯示動態連結重定位資訊。</p>

<p>-s：顯示檔案所有內容。</p>

<p>-S：顯示原始碼和反組合語言程式碼（包含-d引數）。</p>

<p>-W：顯示檔案中包含有DWARF除錯資訊格式的段。</p>

<p>-t：顯示檔案中的符號表。</p>

<p>-T：顯示動態連結符號表。</p>

<p>-x：顯示檔案的所有檔案頭。</p>

<p>A.3.4 cl，MSVC編譯器</p>

<p>/c：只編譯不連結。</p>

<p>/Za：禁止語言擴充套件。</p>

<p>/link：連結指定的模組或給連結器傳遞引數。</p>

<p>/Od：禁止最佳化。</p>

<p>/O2：以執行速度最快為目標最佳化。</p>

<p>/O1：以最節省空間為目標最佳化。</p>

<p>/GR或/GR-：開啟或關閉RTTI。</p>

<p>/Gy：開啟函式級別連結。</p>

<p>/GS或/GS-：開啟或關閉。</p>

<p>/Fa[file]：輸出組譯檔案。</p>

<p>/E：只進行預處理並且把結果輸出。</p>

<p>/I：指定標頭檔包含目錄。</p>

<p>/Zi：啟用除錯資訊。</p>

<p>/LD：編譯產生DLL檔案。</p>

<p>/LDd：編譯產生DLL檔案（除錯版）。</p>

<p>/MD：與動態多執行緒版本執行庫MSVCRT.LIB連結。</p>

<p>/MDd：與除錯版動態多執行緒版本執行庫MSVCRTD.LIB連結。</p>

<p>/MT：與靜態多執行緒版本執行庫LIBCMT.LIB連結。</p>

<p>/MTd：與除錯版靜態多執行緒版本執行庫LIBCMTD.LIB連結。</p>

<p>A.3.5 link，MSVC連結器</p>

<p>/BASE:address：指定輸出檔案的基地址。</p>

<p>/DEBUG：輸出除錯模式版本。</p>

<p>/DEF:filename：指定模組定義檔案.DEF。</p>

<p>/DEFAULTLIB:library：指定預設執行庫。</p>

<p>/DLL：產生DLL。</p>

<p>/ENTRY:symbol：指定程式入口。</p>

<p>/EXPORT:symbol：指定某個符號為匯出符號。</p>

<p>/HEAP：指定預設堆大小。</p>

<p>/LIBPATH:dir：指定連結時庫搜尋路徑。</p>

<p>/MAP[:filename]：產生連結MAP檔案。</p>

<p>/NODEFAULTLIB[:library]：禁止預設執行庫。</p>

<p>/OUT:filename：指定輸出檔名。</p>

<p>/RELEASE：以發布版本產生輸出檔案。</p>

<p>/STACK：指定預設棧大小。</p>

<p>/SUBSYSTEM：指定子系統。</p>

<p>A.3.6 dumpbin，MSVC的COFF/PE檔案檢視器</p>

<p>/ALL：顯示所有資訊。</p>

<p>/ARCHIVEMEMBERS：顯示.LIB檔案中所有目的檔列表。</p>

<p>/DEPENDENTS：顯示檔案的動態連結依賴關係。</p>

<p>/DIRECTIVES：顯示連結器指示。</p>

<p>/DISASM：顯示反組譯。</p>

<p>/EXPORTS：顯示匯出函式表。</p>

<p>/HEADERS：顯示檔案頭。</p>

<p>/IMPORTS：顯示匯入函式表。</p>

<p>/LINENUMBERS：顯示行號資訊。</p>

<p>/RELOCATIONS：顯示重定位資訊。</p>

<p>/SECTION:name ：顯示某個段。</p>

<p>/SECTION：顯示檔案概要資訊。</p>

<p>/SYMBOLS：顯示檔案符號表。</p>

<p>/TLS：顯示執行緒區域性儲存TLS資訊。</p>
