module.exports = {
  apps : [{
    name   : "marvin",
    script : "main.sh",
    watch: true,
    max_memory_restart: "500M",
    autorestart: true,
    max_restarts: 10,
  }]
}
