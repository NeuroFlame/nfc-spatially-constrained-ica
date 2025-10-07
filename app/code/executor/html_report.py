HTML_OUTPUT="""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>GICA Results</title>
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' data: blob: filesystem: *">
  <style>
    html, body {margin:0;height:100%;background:#fff;}
    iframe {border:0;width:100%;height:100%;}
    .msg {color:#eee;font:14px/1.4 system-ui, sans-serif;padding:16px}
  </style>
</head>
<body>
  <div id="fallback" class="msg">Loading results…</div>
  <iframe id="report" hidden></iframe>

  <script>
    (function () {
      const qs = new URLSearchParams(location.search);
      const token = qs.get('x-access-token') || localStorage.getItem('accessToken') || '';
      const windowParam = qs.get('window') || 'self';
      const edgeBase = qs.get('edgeBase');
      const consortiumId = qs.get('consortiumId');
      const runId = qs.get('runId');

      let target;
      if (edgeBase && consortiumId && runId) {
        target = `${edgeBase}/zip/${encodeURIComponent(consortiumId)}/${encodeURIComponent(runId)}/gica_cmd_gica_results/icatb_gica_html_report.html`;
      } else {
        target = `./gica_cmd_gica_results/icatb_gica_html_report.html`;
      }

      // Append auth + window param
      const url = new URL(target, location.href);
      if (token) url.searchParams.set('x-access-token', token);
      if (windowParam) url.searchParams.set('window', windowParam);

      const iframe = document.getElementById('report');
      iframe.src = url.toString();
      iframe.hidden = false;

      const fb = document.getElementById('fallback');
      if (fb) fb.remove();
    })();
  </script>
</body>
</html>
"""
