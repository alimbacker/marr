/* The wedding details the page script uses: calendar, sharing, RSVP, countdown.
   The words shown on screen live in index.html — if you change a time or the
   venue, change it there too. */
window.WEDDING = {
  couple: "Sivaprakash & Manthra Bai",
  dayShort: "Sunday 13 September",
  shareText: "With the blessings of our elders, Sivaprakash & Manthra Bai are getting married on Sunday 13 September 2026 at MAAS Mini Hall, Sivakasi. Muhurtham 8.00–9.00 am.",

  // After the site is online, put its address here so Share sends a working link.
  siteUrl: "",

  muhurtham: { start: "2026-09-13T08:00:00+05:30", end: "2026-09-13T09:00:00+05:30" },
  afterText: "Married on 13 September 2026 · Thank you for your blessings",

  venue: {
    name: "MAAS Mini Hall",
    address: "Ganagiri Road, opposite Allahabad Bank, Sivakasi 626189, Tamil Nadu",
    maps: "https://www.google.com/maps/search/?api=1&query=MAAS%20Mini%20Hall%2C%20Ganagiri%20Road%2C%20Sivakasi%20626189"
  },

  // WhatsApp number that receives replies: country code + number, digits only,
  // e.g. "919876543210". Leave it "" and the RSVP buttons stay hidden.
  rsvpWhatsApp: "",

  // Everything in the "Add to calendar" file. mainEvent = the one Google Calendar opens.
  calendarFile: "sivaprakash-manthra-wedding",
  mainEvent: 1,
  events: [
    { summary: "Welcome & breakfast · Sivaprakash & Manthra Bai", start: "2026-09-13T07:00:00+05:30", end: "2026-09-13T08:00:00+05:30" },
    { summary: "Muhurtham · Sivaprakash & Manthra Bai", start: "2026-09-13T08:00:00+05:30", end: "2026-09-13T09:00:00+05:30",
      note: "Aavani 27 · muhurtham between 8.00 and 9.00 am", remindMinutes: 720 },
    { summary: "Wedding lunch · Sivaprakash & Manthra Bai", start: "2026-09-13T11:30:00+05:30", end: "2026-09-13T14:00:00+05:30" }
  ]
};
