# Reports Folder

Place each published report HTML file in this folder.

The manifest builder reads these meta tags from each report file:

```html
<meta name="report:title" content="2025 IT Statistics">
<meta name="report:client" content="Ministry of Science and ICT">
<meta name="report:year" content="2025">
<meta name="report:type" content="Business">
<meta name="report:sample" content="About 5,000 companies">
<meta name="report:desc" content="Short description for the portal card">
<meta name="report:color" content="#2d82d4">
```

Only `report:title` is strongly recommended. Missing fields fall back to defaults.
