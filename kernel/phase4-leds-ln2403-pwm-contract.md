# LN2403 PWM contract

There is no PWM DT specifier. Stock directly calls the legacy MediaTek API.

Common configuration: `pwm_no=3` (`PWM_3`, GPIO22 mux 1),
`mode=PWM_MODE_OLD`, `clk_div=CLK_DIV1`,
`clk_src=PWM_CLK_OLD_MODE_BLOCK`, `intr=0`, `pmic_pad=0`, and OLD-mode
`IDLE_VALUE=GUARD_VALUE=GDURATION=WAVE_NUM=0`.

| request | DATA_WIDTH | THRESH | pinctrl/GPIO result |
|---|---:|---:|---|
| mode LOW (1) | 17 | floor(97×17/100)=16 | `pwmon`; EN then POWER high |
| mode NORMAL (2) | 17 | floor(73×17/100)=12 | same |
| mode HIGH (3) | 17 | floor(11×17/100)=1 | same |
| brightness N != 0 | 100 | `100-min_signed(N,94)` for normal N | `pwmon`; POWER then EN high |
| off | — | — | disable PWM3 `(3,0)`, select high then low, both gates low |

The generic arithmetic is signed `thresh = percents * data_width / 100`, then
stored into 16-bit OLD-mode fields. Provider returns are ignored. The cached
`pwm_enabled` byte avoids the provider disable call when already off, but the
pinctrl-high selection still occurs. No delay exists in the consumer; the
provider's disable implementation internally delays 1 ms.
