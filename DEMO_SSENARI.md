# Demo ssenarisi (5 dəqiqə)

Demodan əvvəl: `python run.py` ilə serveri işə sal və brauzerdə `http://localhost:8000` aç. **New chat** bas. `.env` faylını bağla (açar ekranda görünməsin). Terminalı ekranın kənarında açıq saxla, orada alət çağırışları görünür.

---

## 0:00–0:30 · Giriş (danış)

> "SuperChat üç köməkçini (uçuş, alış-veriş, kino) bir chat pəncərəsində birləşdirir. İstifadəçi domen seçmir: hər mesajı router avtomatik təsnif edir. Bütün cavablar yalnız rəsmi mock datadan gəlir."

## 0:30–3:30 · Canlı söhbət (domen 4 dəfə dəyişir)

Mesajları ardıcıl yaz. Hər cavabdan sonra altdakı etiketi göstər, məsələn `follow_up · flights`.

| # | Yaz | Göstər / de |
|---|---|---|
| 1 | `Find me a flight from Baku to Istanbul on Friday.` | "Friday 6 noyabrdır. Reyslər ucuzdan bahaya sıralanıb, 'cəmi 3 yer qalıb' xəbərdarlığı datadan gəlir." |
| 2 | `The cheaper one, is it direct?` | "Bu follow-up-dır. Sistem son nəticələrin sırasını yaddaşda saxlayır. Ən ucuz reys 1 aktarmalıdır, bunu düz deyir." |
| 3 | `What is playing tonight?` | **1-ci dəyişmə → kino.** "Deep Signal-ın biletləri satılıb qurtarıb, sistem bunu xüsusi qeyd edir." |
| 4 | `Show me laptops.` | **2-ci dəyişmə → alış-veriş.** |
| 5 | `İkincisi stokda var?` | "Dil dəyişdi, sistem Azərbaycan dilində cavab verir və 'ikincisi' sözünü düzgün başa düşür." |
| 6 | `Okay, and the sci-fi one, any seats on Saturday?` | **3-cü dəyişmə → kinoya qayıdış.** "İki sci-fi film var, ona görə sistem təxmin etmir, soruşur və ya ikisini də göstərir." |
| 7 | `I need a flight to Istanbul on 6 November and a backpack for the trip.` | **4-cü dəyişmə → mixed.** "Bir mesajda iki domen var, iki modul çağırılır, cavab isə tək olur." |
| 8 | `What is the weather in Ganja?` | "Mövzudan kənardır: nəzakətli imtina və nə edə biləcəyini göstərir." |

Sonra **New chat** bas və `Book two seats.` yaz. "Kontekst yoxdur, ona görə sistem kino üçün, yoxsa uçuş üçün olduğunu soruşur."

## 3:30–4:30 · Arxitektura (hesabatdakı diaqramı göstər)

> "Mesaj əvvəlcə routerə gedir. Router LLM ilə kateqoriyanı təyin edir, LLM işləməsə açar sözlərə əsaslanan qaydalar işə düşür. Sonra agent yalnız seçilmiş domenin alətlərini görür. Alətlər datanı repository interfeysləri vasitəsilə oxuyur. 2-ci mərhələdə real API üçün yalnız bir yeni sinif əlavə olunacaq, qalan kod dəyişməyəcək."

## 4:30–5:00 · Test nəticələri

> "Əsas test setində 57 mesajdan 57-si düzgün təsnif olundu. Bu setin asan olduğunu nəzərə alıb yazı səhvləri, qarışıq dil və kontekstsiz mesajlarla 47 mesajlıq çətin set əlavə etdim. Orada nəticə X% oldu, əsas səhvlər bunlar idi: ... Onları belə düzəltdim: ..."

---

## Ehtimal olunan suallar və cavablar

**Niyə hibrid routing seçdin?**
Yalnız qaydalar "the cheaper one" kimi follow-up-ları və üç dili zəif tanıyır. Yalnız LLM ilə isə kateqoriyanı ölçmək olmur. Hibriddə kateqoriya açıq görünür və test olunur. LLM sıradan çıxsa, qaydalar ehtiyat kimi işə düşür.

**Sistemin qiymət uydurmadığını necə təmin edirsən?**
LLM rəqəmləri yalnız alətlərin nəticəsindən götürür. Promptda bu açıq qadağandır. Alət boş qaytaranda sistem "datada tapılmadı" deyir.

**"Back to the headphones" necə işləyir?**
Hər domenin yaddaşı ayrıca obyektdə saxlanılır (`state.py`). Başqa domenə keçəndə köhnə yaddaş silinmir.

**Real API-yə necə keçəcəksən?**
`FlightRepository` interfeysini implement edən yeni `TravelpayoutsFlightRepository` sinfi yazacağam və `.env` faylında `FLIGHT_SOURCE=api` qoyacağam. Router, alətlər və UI dəyişməyəcək.

**Server yenidən başlasa nə olur?**
Yaddaş RAM-da saxlanılır, ona görə söhbətlər və rezervlər silinir. Bu, hesabatın "Məhdudiyyətlər" bölməsində yazılıb. Həlli SQLite istifadə etməkdir.

**Tarixləri necə həll edirsən?**
LLM-ə 2 noyabr 2026-dan başlayan 14 günlük təqvim verilir, hər günün adı yazılıb. Ona görə "Friday" sözünü səhv hesablamır.

**LLM sıradan çıxsa nə olur?**
Router qaydalara keçir. Agent xəta versə, istifadəçi öz dilində qısa üzr mesajı görür, stack trace göstərilmir.
