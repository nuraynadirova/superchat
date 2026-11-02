# SuperChat — Routing test log

Model: `openai/gpt-oss-120b` · Reference date: 2026-11-02 · Turns: 57 in 30 conversations

## Accuracy

- Category accuracy: **57/57 = 100.0%**
- Category + domains accuracy: **57/57 = 100.0%**
- Rule fallback used: 0 times
- Average latency per turn: 19.4 s

### By category

| Category | Correct | Total | Accuracy |
|---|---|---|---|
| ambiguous | 6 | 6 | 100% |
| cinema | 9 | 9 | 100% |
| flights | 7 | 7 | 100% |
| follow_up | 17 | 17 | 100% |
| mixed | 4 | 4 | 100% |
| out_of_scope | 5 | 5 | 100% |
| shopping | 9 | 9 | 100% |

### By language

| Language | Correct | Total | Accuracy |
|---|---|---|---|
| az | 14 | 14 | 100% |
| en | 29 | 29 | 100% |
| mixed-lang | 3 | 3 | 100% |
| ru | 11 | 11 | 100% |

### Confusion (expected → predicted, errors only)

- none

## Errors

- none

## Error analysis

_Write 3–5 sentences here: why the errors happened and what you changed (prompt, rules, examples)._

## Full transcript

**B1.1** User: Find me a flight from Baku to Istanbul on Friday.  
`flights ['flights']` Bot: **Flights Baku → Istanbul on Friday (2026‑11‑06)**    1. **Azerwings AW520** – 05:00 – 10:40, 1 stop (via TBS) – 175 AZN – 11 seats left   2. **Bosphor Air BA220** – 14:20 – 17:00, direct – 245 AZN – 3 seats left (few)   3. **Caspian Air CA101** – 07:30 – 10:05, direct – 289 AZN – 14 seats left    Let me know which one you’d like to book or if you need more details.

**B1.2** User: What is playing tonight?  
`cinema ['cinema']` Bot: **Tonight (2026‑11‑02) – CinemaPlus**  | # | Film | Cinema (district) | Time | Price (AZN) | Seats | |---|------|-------------------|------|-------------|-------| | 1 | **Orbit Zero** (sci‑fi, thriller) | CinemaPlus Ganjlik (Nasimi) | 19:30 | 12.0 | 34 available | | 2 | **Deep Signal** (sci‑fi, mystery) | CinemaPlus 28 Mall (Nasimi) | 20:15 | 13.0 | **SOLD OUT** | | 3 | **Laugh Track** (comedy) | 

**B1.3** User: Do you have wireless headphones under 100 AZN?  
`shopping ['shopping']` Bot: **Wireless headphones under 100 AZN**  - **Sonivo Wireless Headphones** – Black, 89.9 AZN, rating 4.4, 23 in stock.  Let me know if you’d like to add them to your cart or need more options.

**B2.1** User: What is playing tonight?  
`cinema ['cinema']` Bot: **Tonight (2026‑11‑02) – movies playing**  1. **Deep Signal** – sci‑fi, mystery – English – rating 8.4   2. **Orbit Zero** – sci‑fi, thriller – English – rating 8.1   3. **Laugh Track** – comedy – Russian – rating 6.9    Let me know if you’d like showtimes or want to book tickets for any of them.

**B2.2** User: Show me laptops.  
`shopping ['shopping']` Bot: **Laptops in stock**  1. **Laptop 15" Pro** – Nexar, silver, 1899 AZN, rating 4.6, 7 units left.   2. **Laptop 14" Air** – Nexar, grey, 1249 AZN, rating 4.3, 12 units left.    Let me know which one you’d like more details on or want to add to your cart.

**B2.3** User: Okay, and the sci-fi one, any seats on Saturday?  
`follow_up ['cinema']` Bot: Both **Deep Signal** (M008) and **Orbit Zero** (M001) are sci‑fi movies on Saturday (2026‑11‑07). Which one would you like to see seat availability for?

**B3.1** User: Show me laptops.  
`shopping ['shopping']` Bot: **Laptops (in stock)**    1. **Laptop 15" Pro** – Nexar, silver, 1899 AZN, rating 4.6, 7 units left.   2. **Laptop 14" Air** – Nexar, grey, 1249 AZN, rating 4.3, 12 units left.

**B3.2** User: The second one, is it in stock?  
`follow_up ['shopping']` Bot: Yes, the Laptop 14" Air (grey, Nexar) is in stock with 12 units available. Would you like to add it to your cart?

**B4.1** User: Flights to Istanbul on 6 November.  
`flights ['flights']` Bot: Which city would you like to depart from?

**B4.2** User: The cheaper one, is it direct?  
`follow_up ['flights']` Bot: Sure! Could you tell me which city you’ll be flying from?

**B5.1** User: I need a flight to Istanbul on 6 November and a backpack for the trip.  
`mixed ['flights', 'shopping']` Bot: **Flights to Istanbul on 2026‑11‑06**  | # | Airline / Flight | Dep‑time | Arr‑time | Stops | Price (AZN) | Seats left | |---|------------------|----------|----------|-------|-------------|------------| | 1 | Azerwings AW520 | 05:00 | 10:40 | 1 (via TBS) | 175 | 11 | | 2 | Bosphor Air BA220 | 14:20 | 17:00 | Direct | 245 | 3 | | 3 | Caspian Air CA101 | 07:30 | 10:05 | Direct | 289 | 14 |  **Backpa

**B6.1** User: Show me something good.  
`ambiguous []` Bot: What would you like to see – a flight option, a product, or a movie recommendation?

**B7.1** User: What is the weather in Ganja?  
`out_of_scope []` Bot: Sorry, I can't help with that. I can help you find and book flights, shop for products, or find films and cinema showtimes.

**B8.1** User: Book two seats.  
`ambiguous []` Bot: Do you want to book seats for a flight or for a movie?

**E1.1** User: Any comedies this week?  
`cinema ['cinema']` Bot: **Comedies this week (Nov 2 – Nov 8)**    | Movie | Date & Time | Cinema (District) | Price (AZN) | Seats left | |-------|-------------|-------------------|-------------|------------| | **Laugh Track** (Russian) | 02 Nov 2026, 21:00 | CinemaPlus Ganjlik (Nasimi) | 9.0 | 52 | | **Laugh Track** | 08 Nov 2026, 17:30 | CinemaPlus 28 Mall (Nasimi) | 8.0 | 83 | | **Spring in Baku** (Azerbaijani) | 05 No

**E1.2** User: What about in Russian?  
`follow_up ['cinema']` Bot: **Russian‑language comedies this week**  | # | Movie | Date & Time | Cinema (District) | Price (AZN) | Seats left | |---|-------|-------------|-------------------|-------------|------------| | 1 | **Laugh Track** | 02 Nov 2026, 21:00 | CinemaPlus Ganjlik (Nasimi) | 9.0 | 52 | | 2 | **Laugh Track** | 08 Nov 2026, 17:30 | CinemaPlus 28 Mall (Nasimi) | 8.0 | 83 |  Both showtimes have seats available.

**E1.3** User: Book 2 tickets for the first showtime.  
`follow_up ['cinema']` Bot: Your 2 tickets for **“Laugh Track”** (Russian comedy) on **02 Nov 2026 at 21:00** at **CinemaPlus Ganjlik (Nasimi)** are now reserved.  - **Reservation ID:** CR‑BF5774   - **Total price:** 18 AZN    Let me know if you’d like to confirm the reservation, get the ticket details, or need anything else!

**E2.1** User: Compare the Smartphone X5 and X5 Lite.  
`shopping ['shopping']` Bot: **Smartphone X5 vs X5 Lite**  | Feature | X5 | X5 Lite | |---|---|---| | Price | 999 AZN | **549 AZN** (cheaper) | | Rating | 4.5 ★ (best rated) | 4.0 ★ | | Display | 6.5‑inch OLED | 6.1‑inch LCD | | Storage | 128 GB | 64 GB | | Color | Black | Blue | | Stock | 18 units | 31 units (in stock) | | Availability | In stock | In stock | | Description | Dual camera, larger OLED screen | Smaller LCD scre

**E2.2** User: Add the cheaper one to my cart.  
`follow_up ['shopping']` Bot: Added the cheaper **Smartphone X5 Lite** (1 unit) to your cart. Total: **549 AZN**. Let me know if you’d like to view the cart, add anything else, or proceed to checkout.

**E2.3** User: Find me a direct flight to Dubai next week.  
`flights ['flights']` Bot: Sure! To find a direct flight to Dubai next week, could you tell me the departure city (e.g., Baku, Istanbul, etc.)?

**E2.4** User: Back to my cart, what's the total?  
`follow_up ['shopping']` Bot: Your cart contains:  - **Smartphone X5 Lite** – 1 unit × 549 AZN = **549 AZN**  **Total:** **549 AZN**. Let me know if you’d like to add more items, remove something, or proceed to checkout.

**E3.1** User: Can you write me a poem about autumn?  
`out_of_scope []` Bot: Sorry, I can't help with that. I can help you find and book flights, shop for products, or find films and cinema showtimes.

**E4.1** User: Which film has the highest rating, and do you sell a portable speaker?  
`mixed ['cinema', 'shopping']` Bot: **Film with the highest rating:** *Deep Signal* – rating 8.4 (sci‑fi, mystery, English).  **Portable speaker:** Yes. We have the **Sonivo Portable Speaker** (black) for **74.5 AZN**, in stock (40 units).

**E5.1** User: Is there a business class flight to Istanbul?  
`flights ['flights']` Bot: **Business class to Istanbul**  - **Caspian Air CA107** – Baku → Istanbul     - Departure: 2026‑11‑07 18:00 (arrives 20:35)     - Direct, 215 min, 40 kg baggage     - **Price:** 890 AZN     - Seats left: 4    Would you like to reserve a seat on this flight?

**E5.2** User: How much baggage does it include?  
`follow_up ['flights']` Bot: The business‑class flight **Caspian Air CA107** (Baku → Istanbul) includes **40 kg of checked baggage** per passenger.

**E5.3** User: Reserve it for one person.  
`follow_up ['flights']` Bot: Your reservation is confirmed:  - **Flight:** Caspian Air CA107 (Baku → Istanbul)   - **Date & Time:** 2026‑11‑07 18:00 – 20:35   - **Cabin:** Business   - **Passengers:** 1   - **Total price:** 890 AZN   - **Reservation ID:** FR‑B59026    Let me know if you need anything else (e.g., ticket details, travel insurance, or a different flight).

**E6.1** User: Which cinemas do you have in Sumgayit?  
`cinema ['cinema']` Bot: **CinemaPlus Sumgayit**   - District: Sumgayit   - Address: Sumgayit Boulevard Plaza, Sumgayit

**E7.1** User: What's cheap?  
`ambiguous []` Bot: Are you looking for cheap flights, products, or movie tickets?

**E8.1** User: Who won the football match yesterday?  
`out_of_scope []` Bot: Sorry, I can't help with that. I can help you find and book flights, shop for products, or find films and cinema showtimes.

**A1.1** User: Cümə günü Bakıdan İstanbula uçuş tap.  
`flights ['flights']` Bot: Cümə günü (2026‑11‑06) Bakı → İstanbul uçuşları:  1. **Azerwings AW520** – 05:00‑10:40, 1 dayanacaq (TBS), 175 AZN, 11 yer qalıb.   2. **Bosphor Air BA220** – 14:20‑17:00, birbaşa, 245 AZN, 3 yer qalıb.   3. **Caspian Air CA101** – 07:30‑10:05, birbaşa, 289 AZN, 14 yer qalıb.  Hansını seçmək istəyirsiniz? (Rezervasiya üçün sərnişin sayını da bildirin.)

**A1.2** User: Bu axşam kinoda nə var?  
`cinema ['cinema']` Bot: Bu axşam (2026‑11‑02) kinomazada:  - **Orbit Zero** – 19:30, CinemaPlus Ganjlik (Hall 1), 12 AZN, 34 yer qalıb.   - **Deep Signal** – 20:15, CinemaPlus 28 Mall (Hall 3), 13 AZN, **tam dolu**.   - **Laugh Track** – 21:00, CinemaPlus Ganjlik (Hall 2), 9 AZN, 50 yer qalıb.  Hansını seçmək və ya bilet sifariş etmək istəyirsiniz?

**A1.3** User: 100 manatdan ucuz simsiz qulaqlıq varmı?  
`shopping ['shopping']` Bot: Bəli, 100 AZN‑dən aşağı qiymətə **Sonivo Simsiz qulaqlıq** mövcuddur:  - **Qiymət:** 89.9 AZN   - **Rəng:** qara   - **Stok:** 23 ədəd (hələ mövcuddur)  Sifariş vermək və ya səbətə əlavə etmək istəyirsiniz?

**A2.1** User: Noutbukları göstər.  
`shopping ['shopping']` Bot: **Noutbuklar**  1. **Noutbuk 15" Pro** – Nexar, gümüş, 1899 AZN, reytinq 4.6, mövcud: 7 ədəd   2. **Noutbuk 14" Air** – Nexar, boz, 1249 AZN, reytinq 4.3, mövcud: 12 ədəd    Hansı model sizi maraqlandırır? (Seçib səbətə əlavə edə bilərik.)

**A2.2** User: İkincisi stokda var?  
`follow_up ['shopping']` Bot: Bəli, **Noutbuk 14" Air** (P004) stokda var – 12 ədəd mövcuddur.    İstəyirsinizsə, səbətə əlavə edim?

**A2.3** User: Onu səbətə əlavə et.  
`follow_up ['shopping']` Bot: **Səbətiniz yeniləndi**  - Noutbuk 14" Air – 1 ədəd, 1249 AZN  **Cəmi:** 1249 AZN  Başqa bir şey əlavə etmək və ya sifarişinizi tamamlamaq istəyirsiniz?

**A3.1** User: 6 noyabrda İstanbula uçuş və səfər üçün bel çantası lazımdır.  
`mixed ['flights', 'shopping']` Bot: **Uçuşlar (6 Noyabr, Bakı → İstanbul)**   1. **Azerwings AW520** – 05:00‑10:40, 1 dayanış (TBS), 175 AZN, 11 yer qalıb.   2. **Bosphor Air BA220** – 14:20‑17:00, birbaşa, 245 AZN, 3 yer qalıb.   3. **Caspian Air CA101** – 07:30‑10:05, birbaşa, 289 AZN, 14 yer qalıb.    **Səfər üçün bel çantası** – “travel belt” axtarışına uyğun məhsul kataloqda yoxdur.    Başqa bir aksessuar (məsələn, səyahət çant

**A4.1** User: Gəncədə hava necədir?  
`out_of_scope []` Bot: Bağışlayın, bu mövzuda kömək edə bilmirəm. Mən uçuş tapmaq və bron etmək, məhsul seçmək və almaq, həmçinin film və kino seansları ilə kömək edə bilərəm.

**A5.1** User: İki yer bron et.  
`ambiguous []` Bot: Hangi rezervasyonu yapmak istiyorsunuz? Uçuş mu, yoksa sinema bileti mi?

**A6.1** User: Azərbaycan dilində hansı filmlər var?  
`cinema ['cinema']` Bot: Azərbaycan dilində mövcud filmlər:  1. **The Last Caravan** – macəra, dram (7.6) 2. **Spring in Baku** – romantika, komediya (7.4)

**A6.2** User: Şənbə günü seans var?  
`follow_up ['cinema']` Bot: Təəssüf ki, 2026‑11‑07 (şənbə) tarixində Azərbaycan dilində seans verən film yoxdur. Başqa bir dil, tarix və ya janr üzrə axtarış etmək istəyirsiniz?

**A6.3** User: Dubaya ən ucuz uçuş hansıdır?  
`flights ['flights']` Bot: **Ən ucuz uçuş – Dubai**  | № | Aviaşirkət | Nömrə | Gediş | Gəliş | Müddət | Dayanacaq | Qiymət (AZN) | Boş yer | |---|------------|------|------|------|--------|-----------|--------------|---------| | 1 | Bosphor Air | BA730 | 2026‑11‑06 03:30 (Bakı) | 2026‑11‑06 12:30 (Dubay) | 9 saat | 1 (İstanbul) | **390** | 8 yer |  Bu uçuş ən ucuz seçimdir. **Rezervasiya etmək istəyirsiniz?** (səyahətçi sa

**A6.4** User: Ucuz olanın baqajı neçə kq-dır?  
`follow_up ['flights']` Bot: Bu ucuz uçuşda (Bosphor Air, BA730) sərnişin baqajı **20 kg**‑dır. Başqa sualınız var?

**A7.1** User: Mənə yaxşı bir şey göstər.  
`ambiguous []` Bot: Nə axtarırsınız? Film, məhsul, yoxsa uçuş?

**R1.1** User: Найди рейс из Баку в Стамбул на пятницу.  
`flights ['flights']` Bot: Рейсы Баку → Стамбул на пятницу, 06 ноября:  1. **Azerwings AW520** – 05:00 – 10:40, 1 пересадка (Тбилиси), 175 AZN, 11 мест. 2. **Bosphor Air BA220** – 14:20 – 17:00, прямой, 245 AZN, **3 места**. 3. **Caspian Air CA101** – 07:30 – 10:05, прямой, 289 AZN, 14 мест.  Какой рейс вас интересует? (можно сразу указать количество пассажиров для бронирования).

**R1.2** User: Какой из них прямой?  
`follow_up ['flights']` Bot: Прямыми являются:  - **Bosphor Air BA220** – 14:20 – 17:00, 245 AZN, 3 места. - **Caspian Air CA101** – 07:30 – 10:05, 289 AZN, 14 мест.

**R1.3** User: Что идёт в кино сегодня вечером?  
`cinema ['cinema']` Bot: **Кино сегодня (02 ноября) вечером:**  | Фильм | Жанр | Язык | Время | Кинотеатр (район) | Зал | Цена | Мест осталось | |------|------|------|-------|-------------------|----|------|----------------| | **Orbit Zero** | sci‑fi, thriller | English | 19:30 | CinemaPlus Ganjlik (Nasimi) | Hall 1 | 12 AZN | 34 | | **Deep Signal** | sci‑fi, mystery | English | 20:15 | CinemaPlus 28 Mall (Nasimi) | Hall 

**R2.1** User: Покажи ноутбуки.  
`shopping ['shopping']` Bot: **Ноутбуки в наличии**  1. **Ноутбук 15" Pro** – Nexar, серебристый, 1899 AZN, рейтинг 4.6, 7 шт.   2. **Ноутбук 14" Air** – Nexar, серый, 1249 AZN, рейтинг 4.3, 12 шт.    Выберите, какой добавить в корзину.

**R2.2** User: Второй есть в наличии?  
`follow_up ['shopping']` Bot: Да, **Ноутбук 14" Air** (серый, Nexar) есть в наличии — 12 штук. Хотите добавить его в корзину?

**R3.1** User: Мне нужен билет в Москву и кроссовки для бега.  
`mixed ['flights', 'shopping']` Bot: Из какого города и на какую дату вам нужен билет в Москву?

**R4.1** User: Какая погода в Гяндже?  
`out_of_scope []` Bot: Извините, с этим я помочь не могу. Я помогаю найти и забронировать авиабилеты, подобрать товары, а также найти фильмы и сеансы в кино.

**R5.1** User: Забронируй два места.  
`ambiguous []` Bot: Вы хотите забронировать места на рейс или в кино?

**R6.1** User: Покажи комедии.  
`cinema ['cinema']` Bot: Комедии:  1. **Spring in Baku** – азербайджанский, рейтинг 7.4, возраст 12+   2. **Laugh Track** – русский, рейтинг 6.9, возраст 6+    Выберите фильм, чтобы увидеть сеансы.

**R6.2** User: А что есть из наушников?  
`shopping ['shopping']` Bot: **Наушники в наличии**  1. **Беспроводные наушники** – Sonivo, чёрные, 89.9 AZN, рейтинг 4.4, в наличии 23 шт.    Что хотите сделать: добавить в корзину, посмотреть детали или поискать другие модели?

**R6.3** User: Вернёмся к комедиям, есть сеансы в субботу?  
`follow_up ['cinema']` Bot: К сожалению, в субботу (2026‑11‑07) у нас нет сеансов комедий. Хотите посмотреть комедии в другой день?

**X1.1** User: Show me smartwatches.  
`shopping ['shopping']` Bot: **Smartwatch S2** – Veltra   - Price: 199 AZN   - Rating: 4.2 ★   - Color: black   - Stock: 15 units (in stock)    Let me know if you’d like more details, to compare it with another model, or to add it to your cart.

**X1.2** User: Qiyməti neçədir?  
`follow_up ['shopping']` Bot: Qiyməti **199 AZN**‑dir.

**X1.3** User: А какие фильмы идут завтра?  
`cinema ['cinema']` Bot: Завтра (2026‑11‑03) в кинотеатрах идут:  1. **Paper Kites** – анимация, семейный фильм, язык русский, рейтинг 7.8.   2. **Iron Ledger** – боевик/криминал, язык английский, рейтинг 7.0.    Хотите узнать расписание сеансов или забронировать билеты?
