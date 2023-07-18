heroku logs --tail --app simplici7y | gawk '{
  match($1, /([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2})/, a);
  match($0, /method=([A-Z]*)/, b);
  match($0, /path="([^"]*)"/, c);
  match($0, /status=([0-9]*)/, d);
  color = "\033[0m";  # Default color (white)
  if (d[1] >= 200 && d[1] < 300)
    color = "\033[32m";  # Green
  else if (d[1] >= 300 && d[1] < 400)
    color = "\033[33m";  # Yellow
  else if (d[1] >= 400)
    color = "\033[31m";  # Red
  printf "%s %s%s\033[0m %s %s\n", a[1], color, d[1], b[1], c[1]
}'
