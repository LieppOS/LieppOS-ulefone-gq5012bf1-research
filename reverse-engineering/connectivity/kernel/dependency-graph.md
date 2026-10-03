# Connectivity kernel dependency graph (stock `depends=`)

```
                      pmic_lbat_service  pmic_lvsys_notify
                               \            /
                         mtk_low_battery_throttling
                                   |
 aee_aed  mtk_disp_notify  device-apc-common  ccci_md_all           scp  mtk_tinysys_ipi
      \         |                |               |                    |       |
       +--------+-------+--------+---------------+                    |       |
                        |                                             |       |
                     connadp ------------------------------------+    |       |
                        |                                         \   |       |
                   conninfra                                     connscp -----+
          +-------------+--------------+-------------+               |
          |             |              |             |             gps_scp
   fmradio_drv_    gps_drv_dl_v051  bt_drv_6878  wlan_drv_gen4m_6878
     connac2x                       /    |   \        |   |   |   \
                         bluetooth(rfkill) connfem  cfg80211 mddp wmt_chrdev_wifi_connac2
                                                    (rfkill)  (ccci_md_all)
 gps_pwr <- connadp      wifi_cooling <- connadp     mac80211 <- cfg80211, libarc4 (unused by gen4m)
 clkbuf <- spmi-mtk-pmif mt6685-core (none)          uarthub_drv <- mtk_disp_notify (disabled in DT)
 mtk-btcvsd (none; ALSA SCO PCM)
```

Every node drawn above is rebuilt exact, except these external dependencies, which belong to
other scopes: `aee_aed`, `mtk_disp_notify`, `device-apc-common`, `ccci_md_all` (modem), `scp`,
`mtk_tinysys_ipi`, `spmi-mtk-pmif`, `rfkill` (GKI, system_dlkm; exact against GKI) and
`libarc4`. `mtk_low_battery_throttling`, `pmic_lbat_service` and `pmic_lvsys_notify` were made
exact as a dependency of connadp (KDM power_throttling @6df320423600).

Exported-symbol contract (export CRCs exact): conninfra 81, connadp 44, connfem 8,
wmt_chrdev_wifi_connac2 18, connscp 5, uarthub_drv 61, cfg80211 147, mac80211 131,
bluetooth 72, fmradio 1, bt_drv 1, clkbuf 2, mddp 2.
