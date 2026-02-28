# Payslip Email Automator CLI

## CLI Commands (all available)

### Auth

#### Gmail OAuth setup (required before sending emails)
```
python3 -m app.cli auth setup-gmail
```

### Employee

#### Add employee
```
python3 -m app.cli employee add "Full Name" email@example.com 5500000 --designation "Full Stack Developer" --benefit "AI Tools Allowance:336049" --benefit "Courses Allowance:252036" --join-date 2026-01-19
```

#### List employees
```
python3 -m app.cli employee list
```

#### Update employee
```
python3 -m app.cli employee update a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --full-name "Eric Wiyanto" --email wiyantoeric@gmail.com --designation "Full Stack Developer" --salary 5500000 --benefit "AI Tools Allowance:336049" --benefit "Courses Allowance:252036" --join-date 2026-01-19
```

#### Remove employee
```
python3 -m app.cli employee remove a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb
```

### Claims

#### Add claim
```
python3 -m app.cli claim add a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb "AI Tools Allowance - USD 20 (or IDR equivalent)" "cursor invoice.png" --month 2026-02
```

#### Add claim with explicit amount
```
python3 -m app.cli claim add a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb "Courses Allowance - USD 15 (or IDR equivalent)" "course invoice.png" --month 2026-02 --amount 252036
```

#### List claims
```
python3 -m app.cli claim list a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --month 2026-02
```

### Payslips

#### Generate payslip
```
python3 -m app.cli payslip generate a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --month 2026-02
```

#### Generate payslip with worked days
```
python3 -m app.cli payslip generate a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --month 2026-02 --worked-days 20
```

#### Generate payslips for all employees
```
python3 -m app.cli payslip generate-all --month 2026-02
```

#### Send payslip (generates if no PDF provided)
```
python3 -m app.cli payslip send a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --month 2026-02
```

#### Send payslip with existing PDF
```
python3 -m app.cli payslip send a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb --month 2026-02 --pdf output/payslips/a8462a3c-b84f-4ac6-bc42-b8eb3196a0bb-2026-02.pdf
```

#### Send payslips for all employees
```
python3 -m app.cli payslip send-all --month 2026-02
```
