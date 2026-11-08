window.STATE =
{
  "version": 2,
  "slug": "opus-auto",
  "dir": "2026-11-08-opus-auto--wip",
  "title": "Opus и гейты без вмешательства пользователя",
  "mode": "full",
  "depth": "strict",
  "tier": "T1",
  "strictRouting": true,
  "gateSigned": true,
  "sequentialHost": false,
  "isolateTickets": false,
  "briefFile": "2026-11-08-brief.md",
  "memoryFile": "AGENTS.md",
  "memoryOwner": "autopilot",
  "skillDir": "C:/Users/crown/Downloads/Projects/Autopilot/skills/autopilot",
  "baseCommit": null,
  "startedAt": "2026-11-08T16:28:02+01:00",
  "updatedAt": "2026-11-08T16:30:51+01:00",
  "finishedAt": null,
  "stages": [
    {
      "id": "preflight",
      "status": "done",
      "startedAt": "2026-11-08T16:28:02+01:00",
      "finishedAt": "2026-11-08T16:28:09+01:00"
    },
    {
      "id": "manifest",
      "status": "done",
      "startedAt": "2026-11-08T16:28:09+01:00",
      "finishedAt": "2026-11-08T16:28:23+01:00"
    },
    {
      "id": "briefing",
      "status": "skipped",
      "startedAt": "2026-11-08T16:28:23+01:00",
      "finishedAt": "2026-11-08T16:28:30+01:00",
      "note": "полный автомат — самобрифинг"
    },
    {
      "id": "spec",
      "status": "done",
      "startedAt": "2026-11-08T16:28:31+01:00",
      "finishedAt": "2026-11-08T16:30:38+01:00"
    },
    {
      "id": "plan",
      "status": "done",
      "startedAt": "2026-11-08T16:30:38+01:00",
      "finishedAt": "2026-11-08T16:30:51+01:00"
    },
    {
      "id": "build",
      "status": "pending"
    },
    {
      "id": "review",
      "status": "pending"
    },
    {
      "id": "final",
      "status": "pending"
    }
  ],
  "requirements": {
    "total": 8,
    "done": 0,
    "inTicket": 8,
    "inSpec": 0,
    "placeholder": 0,
    "deferred": 0,
    "dropped": 0
  },
  "tickets": [
    {
      "id": "01",
      "title": "ap.py: Opus-ремонт и ревью, подписи, самообновление, гейты",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R06",
        "R07",
        "R08"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/ap.py",
        "tests/test_ap.py"
      ],
      "review": "да — риск: подпись подтверждения Opus и самообновление инструментов",
      "model": "сильная",
      "fingerprint": "db1548cb35559203e789ecd74d110a2d37e11317a5943d9fcc577fc494b090cf",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "01",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profile": "strong",
        "score": 30,
        "factors": {
          "algorithm": 5,
          "coupling": 5,
          "uncertainty": 0,
          "context": 0,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=30; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "ready",
        "fingerprint": "db1548cb35559203e789ecd74d110a2d37e11317a5943d9fcc577fc494b090cf",
        "hostExecutionVerified": false,
        "applied": true
      },
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 30,
        "reason": "score=30; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-01-ap-opus-auto-gates",
        "agentFile": ".claude/agents/autopilot-executor-01-ap-opus-auto-gates.md",
        "profileSha": "65850eba60239f22647c88f0112776dfc0fb340fa6d36c6c46c052c0de1c092b",
        "sig": "d2342560c657151fd7b88acb9472e1210173021b77e85760f6b8142f22a1af5a"
      }
    },
    {
      "id": "02",
      "title": "guard: проверка подписей Opus и ремонтник",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R08"
      ],
      "blockedBy": [],
      "wave": 1,
      "zone": [
        "skills/autopilot/tools/claude_agent_guard.py",
        "tests/test_claude_agent_guard.py"
      ],
      "review": "да — риск: допуск дорогой модели",
      "model": "сильная",
      "fingerprint": "01c50c8af2f39e709e7a6bad218b2ea2eab304908d921e1ec2ee6a838bab3d4c",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "02",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profile": "strong",
        "score": 30,
        "factors": {
          "algorithm": 5,
          "coupling": 5,
          "uncertainty": 0,
          "context": 0,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=30; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "ready",
        "fingerprint": "01c50c8af2f39e709e7a6bad218b2ea2eab304908d921e1ec2ee6a838bab3d4c",
        "hostExecutionVerified": false,
        "applied": true
      },
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 30,
        "reason": "score=30; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-02-guard-opus-signatures",
        "agentFile": ".claude/agents/autopilot-executor-02-guard-opus-signatures.md",
        "profileSha": "daf236de70b248871f7d897f53e9d3e81ad9f21bca1fde1b3e5ca98c0ac4533e",
        "sig": "130b9c41f6e0034cbddeec22db1c74822c8943d9a300f6b0fecc7cb930fa0cad"
      }
    },
    {
      "id": "03",
      "title": "Фазы и документы",
      "requirements": [
        "R01",
        "R02",
        "R03",
        "R04",
        "R05",
        "R06",
        "R07",
        "R08"
      ],
      "blockedBy": [
        "01",
        "02"
      ],
      "wave": 2,
      "zone": [
        "skills/autopilot/phases/",
        "skills/autopilot/SKILL.md",
        "docs/autopilot/",
        "CHANGELOG.md",
        "tests/test_dashboard_views.py"
      ],
      "review": "нет",
      "model": "обычная",
      "fingerprint": "38ebe8c8d9e7a4d48d6e23f59d5ba446427ed5ee82eccc14d04ebb69a61d34af",
      "status": "pending",
      "retries": 0,
      "repairs": 0,
      "plannedRouting": {
        "ticket": "03",
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "profile": "strong",
        "score": 50,
        "factors": {
          "algorithm": 5,
          "coupling": 20,
          "uncertainty": 0,
          "context": 5,
          "testing": 10,
          "risk": 10
        },
        "reason": "score=50; profile=strong; high-risk=True",
        "requiresReview": true,
        "status": "ready",
        "fingerprint": "38ebe8c8d9e7a4d48d6e23f59d5ba446427ed5ee82eccc14d04ebb69a61d34af",
        "hostExecutionVerified": false,
        "applied": true
      },
      "routing": {
        "provider": "anthropic",
        "model": "sonnet",
        "effort": "high",
        "effortEnforced": true,
        "score": 50,
        "reason": "score=50; profile=strong; high-risk=True",
        "verified": true,
        "agentType": "autopilot-executor-03-phases-docs-opus-auto",
        "agentFile": ".claude/agents/autopilot-executor-03-phases-docs-opus-auto.md",
        "profileSha": "37970a42a04f59791aca5b5b588c04f557232eaaeaf4ac5fb105b30a12e80b57",
        "sig": "3ebd9ae70612dbd03989d77018c83db6726c39d230c331e9411b7365dbea2119"
      }
    }
  ],
  "tests": null,
  "usageEvents": [],
  "budgetTokens": null,
  "debt": {
    "placeholders": [],
    "assumptions": [],
    "emptyEnv": []
  },
  "additions": [],
  "coverage": null,
  "concerns": [],
  "blockingFindings": [],
  "blind": null,
  "beats": [
    "2026-11-08T16:28:02+01:00",
    "2026-11-08T16:28:09+01:00",
    "2026-11-08T16:28:23+01:00",
    "2026-11-08T16:28:30+01:00",
    "2026-11-08T16:28:31+01:00",
    "2026-11-08T16:30:01+01:00",
    "2026-11-08T16:30:38+01:00",
    "2026-11-08T16:30:39+01:00",
    "2026-11-08T16:30:40+01:00",
    "2026-11-08T16:30:51+01:00"
  ],
  "rev": 13,
  "waiting": null,
  "waits": [],
  "log": [
    {
      "t": "2026-11-08T16:28:02+01:00",
      "k": "init"
    },
    {
      "t": "2026-11-08T16:28:09+01:00",
      "k": "stage",
      "id": "manifest",
      "act": "start"
    },
    {
      "t": "2026-11-08T16:28:23+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "start"
    },
    {
      "t": "2026-11-08T16:28:30+01:00",
      "k": "stage",
      "id": "briefing",
      "act": "skip",
      "note": "полный автомат — самобрифинг"
    },
    {
      "t": "2026-11-08T16:28:31+01:00",
      "k": "gate",
      "g": "G1",
      "ok": false,
      "open": 8,
      "total": 8
    },
    {
      "t": "2026-11-08T16:28:31+01:00",
      "k": "stage",
      "id": "spec",
      "act": "start"
    },
    {
      "t": "2026-11-08T16:30:01+01:00",
      "k": "tier",
      "v": "T1"
    },
    {
      "t": "2026-11-08T16:30:01+01:00",
      "k": "gate",
      "g": "G1",
      "ok": true,
      "open": 0,
      "total": 8
    },
    {
      "t": "2026-11-08T16:30:38+01:00",
      "k": "stage",
      "id": "plan",
      "act": "start"
    },
    {
      "t": "2026-11-08T16:30:39+01:00",
      "k": "tickets",
      "n": 3
    },
    {
      "t": "2026-11-08T16:30:40+01:00",
      "k": "gate",
      "g": "G3",
      "ok": true,
      "problems": 0
    },
    {
      "t": "2026-11-08T16:30:51+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": false,
      "tickets": 3,
      "blocked": 3
    },
    {
      "t": "2026-11-08T16:30:51+01:00",
      "k": "stage",
      "id": "plan",
      "act": "done"
    },
    {
      "t": "2026-11-08T16:30:51+01:00",
      "k": "plan-models",
      "provider": "anthropic",
      "applied": true,
      "tickets": 3,
      "blocked": 0
    }
  ],
  "reqList": [
    {
      "id": "R01",
      "text": "«Давай доработаем.»",
      "status": "in-ticket"
    },
    {
      "id": "R02",
      "text": "«Все должно работать в автоматическом режиме.»",
      "status": "in-ticket"
    },
    {
      "id": "R03",
      "text": "«Без вмешательства пользователя.»",
      "status": "in-ticket"
    },
    {
      "id": "R04",
      "text": "«Opus-ремонт и ревью ветки»",
      "status": "in-ticket"
    },
    {
      "id": "R05",
      "text": "«Подпись opusAgents в guard»",
      "status": "in-ticket"
    },
    {
      "id": "R06",
      "text": "«Автообновление .autopilot/.py»",
      "status": "in-ticket"
    },
    {
      "id": "R07",
      "text": "«Гейты не сбрасываются зря»",
      "status": "in-ticket"
    },
    {
      "id": "R08",
      "text": "«Оставить (Recommended)» — подтверждение Opus и цитата --by-user по-прежнему от пользователя",
      "status": "in-ticket"
    }
  ],
  "gates": {
    "G1": {
      "ok": true,
      "at": "2026-11-08T16:30:01+01:00",
      "open": 0,
      "total": 8
    },
    "G3": {
      "ok": true,
      "at": "2026-11-08T16:30:40+01:00",
      "problems": 0
    }
  },
  "result": null,
  "gateMark": "3927b3198bb4f1b4109c5c59a3be44d104dbb95dde1848afe670d789e3af83fe",
  "skillVersion": "2.7.0",
  "planContractDigest": "7b5e6fd85833c9fe460af40465f78c5d43cfcd60d4e29a2a39816052aadea0d3",
  "planValidationDigest": "a988eec0e02603cad1c11aa607110ccfcb6f2909e4228f91474bee765ab7c8ed",
  "roleAgents": {
    "reviewer": {
      "agentType": "autopilot-reviewer-2026-11-08-opus-auto",
      "agentFile": ".claude/agents/autopilot-reviewer-2026-11-08-opus-auto.md",
      "model": "sonnet",
      "effort": "high",
      "effortEnforced": true,
      "profileSha": "b8abe524ff87a20dc0e62e5f6349a13efbbba51573f4c767be853ae5316f0cd6"
    },
    "acceptance": {
      "agentType": "autopilot-acceptance-2026-11-08-opus-auto",
      "agentFile": ".claude/agents/autopilot-acceptance-2026-11-08-opus-auto.md",
      "model": "sonnet",
      "effort": "medium",
      "effortEnforced": true,
      "profileSha": "810c985fb95051ea24b859f1a976e4b0ef70f66440ae82590d5b63b42f42ffa6"
    },
    "explorer": {
      "agentType": "autopilot-explorer-2026-11-08-opus-auto",
      "agentFile": ".claude/agents/autopilot-explorer-2026-11-08-opus-auto.md",
      "model": "haiku",
      "effort": "low",
      "effortEnforced": true,
      "profileSha": "1de311157dad0527d5cac748495aa30d36d187f910d7a95eb461de8befb65391"
    }
  },
  "repairAgent": {
    "agentType": "autopilot-executor-repair-2026-11-08-opus-auto",
    "agentFile": ".claude/agents/autopilot-executor-repair-2026-11-08-opus-auto.md",
    "model": "sonnet",
    "effort": "high",
    "effortEnforced": true,
    "profileSha": "3523976ce3993bc40965caae0db449bdd73f0c64935fab5580ce5d6541f0778b"
  }
}
