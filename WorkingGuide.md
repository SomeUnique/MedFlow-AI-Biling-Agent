# Team Working Guide — MedFlow AI

Yeh team guide hai hamare project ke liye. Isko har member follow kare. Roman Urdu mein likha gaya hai taake sab ko aasani se samajh aaye.

---

## Hamara Project (Kya Bana Rahe Hain?)

Hum ek **AI Hospital Management System** bana rahe hain jiska naam hai **MedFlow AI**.

Ye system ek aam hospital ke kaam ko AI agents ki madad se manage karta hai. Aik user (jaise receptionist, doctor, ya manager) system se baat karta hai, aur system AI ke zariye us ka kaam kar deta hai — jaise appointment book karna, patient dhoondna, bed check karna, billing karna, vaghera.

### System ke 5 hisse (components):

| # | Component | Kaam |
|---|-----------|------|
| 1 | Hospital Operations Backend | Hospital ka data aur APIs — hospitals, departments, doctors, patients, appointments, staff, rooms, beds, bed assignments, capacity, availability, emergency operations. Ye system ka "source of truth" hai (sahi data yahi rehta hai). |
| 2 | Brain / Orchestrator Agent | AI ka dimaag — user ka sawaal samajhta hai, intent pehchanta hai, aur request ko sahi specialist agent ko route karta hai. |
| 3 | Billing & Insurance Agent | Billing workflows, insurance info, claim preparation, claim status, rejected claims, financial operations. |
| 4 | Patient Care / Clinical Support Agent | Patient ki symptoms/intake, basic triage/urgency support, department/doctor routing. (Medical diagnosis Nahi karta.) |
| 5 | Reception / Patient Access Agent | Patient registration, appointment booking, doctor lookup, check-in/check-out, reception queries. |

**Asli code root folder mein nahi hai.** Har component apni apni branch par hai. Root par sirf WorkingGuide (ye file) rahegi.

---

## Team Roles (Kon Kia Karega)

| Member | Branch | Component / Kaam |
|--------|--------|------------------|
| **Fatimah** (Project Leader) | `fatimah` | Hospital Operations Backend — poora data aur APIs banati hai, architecture aur code review karti hai. |
| **Nameera** | `nameera` | Brain / Orchestrator Agent — AI ka jo routing aur coordination karta hai. |
| **Zarwish** | `zarwish` | Billing & Insurance Agent — billing aur insurance ka AI. |
| **Minal** | `minal` | Patient Care / Clinical Support Agent — patient intake aur triage ka AI. |
| **Sumiya** | `sumiya` | Reception / Patient Access Agent — patient registration aur appointment booking ka AI. |

---

## Zaroori Rules (Hamesha Yaad Rakho)

1. **Apni branch par kaam karo** — kabhi bhi `main` par direct code mat daalo.
2. **Koee doosre ka data/component copy mat karo** — har member apna hissa alag banata hai.
3. **Components aapas mein APIs/contracts se bat karte hain** — seedhe doosre ki files mein mat ghuso.
4. **Apni responsibility khud test aur document karo.**
5. **Kisi aur ke component ko touch karne se pehle usse baat karo aur team approval lo.**
6. WorkingGuide (ye file) sab ki shared file hai — ye root par rehti hai, baaki code branches par.

---

## Daily Kaam Ka Tarika

```
1. Apni branch par jao
2. main ka latest code lo (working guide update ke liye)
3. Apna kaam karo
4. Commit karo (achha message likho)
5. Apni branch push karo
6. PR banao aur merge karwao
```

Commands:
```bash
git checkout apna-branch-name        # apni branch par jao
git pull origin main                 # working guide update lo
git add .
git commit -m "kya kiya"
git push origin apna-branch-name
```

---

## Main Branch Kaise Use Hoti Hai

- `main` par sirf **WorkingGuide** rehta hai (team ka shared document).
- Har member ka asli code apni apni branch par hota hai.
- Jab koi member ka kaam complete ho jaye, toh wo **Pull Request (PR)** banata hai aur leader (Fatimah) usko review karke merge karti hai.

---

**Best of Luck! Mil ke achha AI Hospital System banate hain!**
