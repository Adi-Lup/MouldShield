# T20 - PDF report

1. Start START_MOULDSHIELD.bat and open My report.
2. Choose English, Română or Polski and generate the explanation. If it has not been generated, Download PDF requests it first.
3. Edit the landlord letter. The backend letter is English; the explanation uses the selected language.
4. Click Download PDF. If your browser does not start saving automatically, click the visible Save PDF link.
5. Open the file and review it before sharing. The existing Print / save PDF button is also available. Nothing is sent to the landlord automatically.

The PDF is generated in your browser with bundled jsPDF and Unicode fonts. No npm/pip/CDN is needed to use it. It contains the reading timestamp, exact humidity alongside the rounded display value, temperature, risk, chain-check result, explanation and edited letter. Demo reports are clearly marked on every page. It blocks export when the explanation is unavailable or the selection changed during generation. If T18 has added selected photos to #photo-report, the exporter includes those visible selected images and their descriptions; it does not fetch all photo history or private GPS metadata.

The implementation follows GitHub issue #20 (US3). Publication and teammate review are still needed for the team's Definition of Done.
