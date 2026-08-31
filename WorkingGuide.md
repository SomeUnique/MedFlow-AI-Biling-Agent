# Team Working Guide - GitHub Collaboration

Yeh guide hai hamare project mein kaise kaam karna hai. Sab log isko follow karein.

---

## Hamara Team

| Member | Branch Name | Role |
|--------|-------------|------|
| Fatima (Project Leader) | `main` | Backend API, Architecture, Code Review |
| Nameera | `nameera` | Frontend / UI |
| Zarwish | `zarwish` | AI Agent / LLM Integration |
| Minal | `minal` | Database / Backend |
| Sumiya | `sumiya` | Testing / QA |

> **Note:** Har member ki apni branch hai. Kabhi bhi `main` pe direct push mat karo.

---

## Hamara Goal

Hum sab mil ke ek project bana rahe hain. Sab log ek hi repository mein kaam karein gi, lekin har kisi ki **apni alag branch** hogi. Jab kaam ho jaye toh hum usko **main branch** mein merge kar dein ge.

---

## Step 1: Repository Access

- Main (Project Leader) ne sab ko repository ka access de diya hai
- Jab tumhe email aaye "You've been invited as a collaborator" toh **Accept** karo
- Accept karne ke baad repository clone karo:

```bash
git clone https://github.com/username/project-name.git
```

---

## Step 2: Apni Branch Banao

Jab bhi koi naya kaam shuru karo, pehle apni branch banao. **Kabhi bhi main branch pe direct kaam mat karo.**

```bash
git checkout -b tumhari-branch-name
```

Branch naming example:
- `rida-feature` 
- `sahiba-fix-login`
- `ayesha-homepage`

Apna naam ya kaam ka naam do, jo samajh aaye.

---

## Step 3: Kaam Karo

Ab apni branch pe kaam karo. Code likho, files banao, jo karna hai karo.

---

## Step 4: Commit Karo

Jab kaam ka ek hissa ho jaye toh usko save (commit) karo:

```bash
git add .
git commit -m "yahan pe likho kya kiya hai"
```

Commit message meaningful likho. For example:
- `"login page bana diya"`
- `"header fix kar diya"`
- `"database connect kar diya"`

Aise mat likho: `"asdfgh"` ya `"done"` - yeh samajh nahi aata kya kiya.

---

## Step 5: Push Karo

Apni branch ko GitHub pe bhejo:

```bash
git push origin tumhari-branch-name
```

---

## Step 6: Pull Request (PR) Banao

Yeh sab se important step hai. Push karne ke baad GitHub website pe jao:

1. Repository kholo
2. **Pull Requests** tab pe click karo
3. **New Pull Request** pe click karo
4. **Base:** main select karo
5. **Compare:** apni branch select karo
6. **Create Pull Request** pe click karo
7. Title mein likho kya kaam kiya hai
8. **Create** pe click karo

---

## Step 7: Code Review aur Merge

- Baaki team members PR dekhein
- Agar sab theek hai toh **Approve** karein
- Phir **Merge** button dabayein
- Merge hone ke baad tumhari branch ka code main mein aa jayega

---

## Important Rules - Yeh Hamesha Yaad Rakho

| Rule | Kyun Zaroori Hai |
|------|------------------|
| Main branch pe kabhi direct push mat karo | Sab ka code kharab ho sakta hai |
| Hamesha apni branch se kaam karo | Conflicts nahi aayein ge |
| Commit message achha likho | Baad mein pata chale kya kiya tha |
| Push se pehle pull karo | Tumhara code purana na rahe |
| PR banake merge karo | Team review kar sake |

---

## Daily Kaam Ka Tarika (Roz Follow Karo)

Yeh tarika har din follow karo jab bhi kaam pe ao:

```
1. Apni branch pe jao
2. Main ka latest code lo
3. Main ka code apni branch mein merge karo
4. Kaam karo
5. Commit karo
6. Push karo
7. PR banao
8. Merge karo
```

Commands:
```bash
git checkout main
git pull origin main
git checkout apni-branch-name
git merge main
# ... ab kaam karo ...
git add .
git commit -m "kya kiya hai"
git push origin apni-branch-name
```

---

## Conflicts Agar Aa Jaye

Agar tumhe error aaye "merge conflict" ka matlab hai do log ne same file mein kuch change kar diya. 

- Tension mat lo, yeh normal hai
- File kholo, dekho kya changes hain
- Jo sahi hai wo rakho, jo galat hai wo hatao
- Phir commit karo

Agar samajh na aaye toh team member se pooch lo.

---

## Quick Commands Reference

| Kaam | Command |
|------|---------|
| Clone repository | `git clone URL` |
| Apni branch banao | `git checkout -b branch-name` |
| Branch switch karo | `git checkout branch-name` |
| Status check karo | `git status` |
| Files add karo | `git add .` |
| Commit karo | `git commit -m "message"` |
| Push karo | `git push origin branch-name` |
| Pull karo | `git pull origin main` |
| Branch list dekho | `git branch` |

---

## Koi Problem Aaye Toh

- Sab se pehle team members se baat karo
- GitHub Issues mein problem likho
- Screenshots lo agar error aaye
- Akele mat lado, team se help lo

---

**Best of Luck! Mil ke achha project banate hain!**

---

## Team Responsibilities — Hospital AI System

The project is divided into 5 independent components. Each member must work only inside their assigned component/folder and communicate with other components through clearly defined APIs/contracts.

### 1. Hospital Operations — Fatimah

Build and maintain the Hospital Operations backend and APIs. This includes hospitals, departments, doctors, patients, appointments, staff, rooms, beds, bed assignments, hospital capacity, doctor/bed availability, emergency operations, patient location and operational search. This service is the operational source of truth for the hospital system.

### 2. Brain / Orchestrator Agent — Member 1

Build the central AI orchestrator that receives the user's request, identifies the user's intent, maintains conversation context and routes the request to the correct specialist agent. It should coordinate responses from Hospital Operations, Billing & Insurance, Patient Care and Reception agents without duplicating their business logic.

### 3. Billing & Insurance Agent — Member 2

Build the billing and insurance specialist. It should handle billing workflows, insurance information/eligibility, claim preparation, claim status, rejected claims and related hospital financial/insurance operations. It must communicate with the Hospital Operations service through its documented APIs when hospital/patient/appointment data is required.

### 4. Patient Care / Clinical Support Agent — Member 3

Build the patient-care specialist for intake and clinical-support workflows. It should handle patient symptoms/intake, basic urgency/triage support, department or doctor routing and patient-care workflow coordination. It must NOT provide medical diagnosis or replace a qualified medical professional.

### 5. Reception / Patient Access Agent — Member 4

Build the reception and patient-access specialist. It should handle patient registration, appointment booking, doctor lookup, check-in/check-out and common reception queries. It should use Hospital Operations APIs for doctors, patients, departments and appointments instead of maintaining duplicate hospital data.

### Integration Rule

The Hospital Operations backend, Billing & Insurance, Patient Care, Reception and Brain/Orchestrator components must remain clearly separated.

- Do NOT duplicate another member's business logic or database.
- Cross-component communication must happen through documented APIs/contracts.
- Each member is responsible for their own tests, documentation and integration contract.
- Before modifying another member's component, coordinate with that member and get team approval.
