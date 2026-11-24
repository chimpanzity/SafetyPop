import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, RotateCcw, Activity } from 'lucide-react';

// ===================================================================
// CONSTANTS
// ===================================================================

const CANONICAL_60 = [
  'A1L','A1R','A2L','A2R','A3L','A3R',
  'A4L','A4R','A5L','A5R','A6L','A6R',
  'B1L','B1R','B2L','B2R','B3L','B3R',
  'C1L','C1R','C2L','C2R','C3L','C3R',
  'D1L','D1R','D2L','D2R','D3L','D3R',
  'E0L','E0R',
  'F1L','F1R','F2L','F2R','F3L','F3R',
  'G0L','G0R',
  'H0L','H0R',
  'I1L','I1R','I2L','I2R','I3L','I3R',
  'I4L','I4R','I5L','I5R','I6L','I6R',
  'J1L','J1R','J2L','J2R','J3L','J3R'
];

const FACE_EMOJI = { Happy: '😊', Angry: '😠', Fearful: '😨', Neutral: '😐' };

// Distractor timeout (ms) — matches VB
const DISTRACTOR_TIMEOUT = 500;
// Stage transition (ms) — brief vanish after correct target touch
const STAGE_TRANSITION = 350;
// Inter-trial delay (ms)
const ITI = 800;

// ===================================================================
// SEEDED RNG (mulberry32) for fixed-sequence mode
// ===================================================================

function mulberry32(seed) {
  return function() {
    seed = (seed + 0x6D2B79F5) | 0;
    let t = seed;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffleWith(arr, rng) {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

const shuffle = (arr) => shuffleWith(arr, Math.random);
const shuffleSeeded = (arr, seed) => shuffleWith(arr, mulberry32(seed));

// ===================================================================
// TRIAL PARSING
// ===================================================================

function parseTrialCode(code) {
  const type = code[0];
  const faceCode = code[1];
  const side = code[2];

  let bubN = 0, oddN = 0;
  if (type === 'A') { bubN = 4; oddN = 4; }
  else if (type === 'B') { bubN = 8; oddN = 4; }
  else if (type === 'C') { bubN = 4; oddN = 8; }
  else if (type === 'D') { bubN = 8; oddN = 8; }
  else if (type === 'G') { bubN = 4; oddN = 0; }
  else if (type === 'H') { bubN = 8; oddN = 0; }
  else if (type === 'I') { bubN = 0; oddN = 4; }
  else if (type === 'J') { bubN = 0; oddN = 8; }

  let leftTask = 'None', rightTask = 'None';
  if (['A','B','C','D'].includes(type)) {
    leftTask = side === 'R' ? 'Bubble' : 'Oddity';
    rightTask = side === 'R' ? 'Oddity' : 'Bubble';
  } else if (type === 'E') {
    leftTask = 'Bubble'; rightTask = 'Bubble';
  } else if (type === 'F') {
    leftTask = 'Oddity'; rightTask = 'Oddity';
  } else if (['G','H'].includes(type)) {
    leftTask = side === 'R' ? 'None' : 'Bubble';
    rightTask = side === 'R' ? 'Bubble' : 'None';
  } else if (['I','J'].includes(type)) {
    leftTask = side === 'R' ? 'None' : 'Oddity';
    rightTask = side === 'R' ? 'Oddity' : 'None';
  }

  let face = '', isProbe = false;
  if (faceCode === '1') face = 'Happy';
  else if (faceCode === '2') face = 'Angry';
  else if (faceCode === '3') face = 'Fearful';
  else if (faceCode === '4') { face = 'Happy'; isProbe = true; }
  else if (faceCode === '5') { face = 'Angry'; isProbe = true; }
  else if (faceCode === '6') { face = 'Fearful'; isProbe = true; }

  return { code, type, faceCode, side, bubN, oddN, leftTask, rightTask, face, isProbe };
}

// ===================================================================
// POSITION GENERATION
// ===================================================================

function generatePositions(parsed) {
  const { type, side, bubN, oddN } = parsed;
  const allCells = [];
  for (let i = 1; i <= 12; i++) allCells.push(i);
  const shuffled = shuffle(allCells);

  let leftPos = [], rightPos = [], targetCellIndex = -1;
  let fTargetPath = [];

  if (['A','B','C','D'].includes(type)) {
    const maxC = Math.max(bubN, oddN);
    const minC = Math.min(bubN, oddN);
    const bigSet = shuffled.slice(0, maxC);
    const smallSet = shuffle(bigSet).slice(0, minC);
    const isBubBig = bubN >= oddN;
    const bubPos = isBubBig ? bigSet : smallSet;
    const oddPos = isBubBig ? smallSet : bigSet;

    if (side === 'R') { leftPos = bubPos; rightPos = oddPos; }
    else { leftPos = oddPos; rightPos = bubPos; }

    const overlapShuffled = shuffle(smallSet);
    const targetCell = overlapShuffled[0];
    const oddPositions = side === 'R' ? rightPos : leftPos;
    targetCellIndex = oddPositions.indexOf(targetCell);
  } else if (type === 'E') {
    const big8 = shuffled.slice(0, 8);
    const small4 = shuffle(big8).slice(0, 4);
    if (side === 'L') { leftPos = small4; rightPos = big8; }
    else { leftPos = big8; rightPos = small4; }
  } else if (type === 'F') {
    const big8 = shuffled.slice(0, 8);
    const small4 = shuffle(big8).slice(0, 4);
    if (side === 'L') { leftPos = small4; rightPos = big8; }
    else { leftPos = big8; rightPos = small4; }
    const overlapCells = shuffle(small4);
    const eightOnly = shuffle(big8.filter(c => !small4.includes(c)));
    fTargetPath = [...overlapCells, ...eightOnly];
    const tCell = fTargetPath[0];
    targetCellIndex = leftPos.indexOf(tCell);
  } else if (['G','H'].includes(type)) {
    const pos = shuffled.slice(0, bubN);
    if (side === 'R') rightPos = pos; else leftPos = pos;
  } else if (['I','J'].includes(type)) {
    const pos = shuffled.slice(0, oddN);
    if (side === 'R') rightPos = pos; else leftPos = pos;
    targetCellIndex = Math.floor(Math.random() * oddN);
  }

  return { leftPos, rightPos, targetCellIndex, fTargetPath };
}

// ===================================================================
// BUILD INITIAL STIMS FOR A TRIAL
// ===================================================================

function buildStims(parsed, positions) {
  const { type, leftTask, rightTask, face, isProbe } = parsed;
  const { leftPos, rightPos, targetCellIndex } = positions;

  const makeStim = (cell, kind, side, idx, isTarget) => ({
    cell,
    side,
    idx,
    kind, // 'Bubble' | 'Target' | 'Distractor'
    alive: true,
    enabled: true,
    isTarget,
    face,
    isProbe
  });

  let leftStims = [];
  let rightStims = [];

  // LEFT SIDE
  if (leftTask === 'Bubble') {
    leftStims = leftPos.map((c, i) => makeStim(c, 'Bubble', 'L', i, false));
  } else if (leftTask === 'Oddity') {
    if (type === 'F') {
      // F: left side has its own target
      leftStims = leftPos.map((c, i) =>
        makeStim(c, i === targetCellIndex ? 'Target' : 'Distractor', 'L', i, i === targetCellIndex));
    } else {
      // Standard oddity on left
      leftStims = leftPos.map((c, i) =>
        makeStim(c, i === targetCellIndex ? 'Target' : 'Distractor', 'L', i, i === targetCellIndex));
    }
  }

  // RIGHT SIDE
  if (rightTask === 'Bubble') {
    rightStims = rightPos.map((c, i) => makeStim(c, 'Bubble', 'R', i, false));
  } else if (rightTask === 'Oddity') {
    if (type === 'F') {
      // F: right side has its own independent target (starts at same overlap cell as left)
      const leftFirstTargetCell = leftPos[targetCellIndex];
      const rightTargetIdx = rightPos.indexOf(leftFirstTargetCell);
      rightStims = rightPos.map((c, i) =>
        makeStim(c, i === rightTargetIdx ? 'Target' : 'Distractor', 'R', i, i === rightTargetIdx));
    } else {
      // For A-D where right is oddity (side='R'), targetCellIndex is into rightPos
      rightStims = rightPos.map((c, i) =>
        makeStim(c, i === targetCellIndex ? 'Target' : 'Distractor', 'R', i, i === targetCellIndex));
    }
  }

  return { leftStims, rightStims };
}

// ===================================================================
// STIMULUS RECTANGLE COMPONENT
// ===================================================================

function StimRect({ stim, onTouch, cellSize, disabled }) {
  if (!stim.alive) return null;
  const row = Math.floor((stim.cell - 1) / 3);
  const col = (stim.cell - 1) % 3;

  const isBubble = stim.kind === 'Bubble';
  const isTarget = stim.kind === 'Target';
  const isDistractor = stim.kind === 'Distractor';

  // Visual styling
  let bg, glyph, inverted;
  if (isBubble) {
    bg = 'linear-gradient(135deg, #67e8f9 0%, #06b6d4 100%)';
    glyph = FACE_EMOJI.Neutral;
    inverted = true; // bubbles are inverted neutral
  } else if (isTarget) {
    bg = 'linear-gradient(135deg, #fde68a 0%, #f59e0b 100%)';
    glyph = FACE_EMOJI[stim.face] || FACE_EMOJI.Neutral;
    inverted = false; // targets are upright emotional
  } else if (isDistractor) {
    bg = 'linear-gradient(135deg, #fde68a 0%, #f59e0b 100%)';
    if (stim.isProbe) {
      glyph = FACE_EMOJI[stim.face] || FACE_EMOJI.Neutral;
      inverted = true; // probe distractors are inverted same-emotion
    } else {
      glyph = FACE_EMOJI.Neutral;
      inverted = false; // standard distractors are upright neutral
    }
  }

  const padding = 8;
  const inner = cellSize - 2 * padding;

  return (
    <div
      onPointerDown={() => !disabled && stim.enabled && onTouch(stim)}
      onPointerEnter={(e) => {
        // Mirrors MC1/SafetyPop VB pattern: enter-event triggers a touch.
        // On touchscreens this means finger sliding across stims fires each
        // one (the chimp-slide behavior). On mouse, we require a button held
        // so drag-with-button mimics finger contact; pure hover doesn't fire.
        if (e.buttons > 0 && !disabled && stim.enabled) onTouch(stim);
      }}
      style={{
        position: 'absolute',
        left: col * cellSize + padding,
        top: row * cellSize + padding,
        width: inner,
        height: inner,
        background: bg,
        borderRadius: 12,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: Math.floor(inner * 0.6),
        cursor: stim.enabled && !disabled ? 'pointer' : 'default',
        opacity: stim.enabled ? 1 : 0.35,
        transform: inverted ? 'rotate(180deg)' : 'none',
        boxShadow: '0 4px 14px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.4)',
        userSelect: 'none',
        transition: 'opacity 150ms ease',
        touchAction: 'none'
      }}
    >
      {glyph}
    </div>
  );
}

// ===================================================================
// TASK GRID (left or right)
// ===================================================================

function TaskGrid({ stims, onTouch, cellSize, label, disabled }) {
  // 3 columns x 4 rows grid
  const gridW = 3 * cellSize;
  const gridH = 4 * cellSize;
  return (
    <div style={{
      position: 'relative',
      width: gridW,
      height: gridH,
      background: 'rgba(255,255,255,0.02)',
      borderRadius: 8,
      border: '1px solid rgba(255,255,255,0.05)'
    }}>
      {stims.map((s, i) => (
        <StimRect key={`${s.side}-${i}-${s.cell}`} stim={s} onTouch={onTouch}
          cellSize={cellSize} disabled={disabled} />
      ))}
      <div style={{
        position: 'absolute', bottom: -22, left: 0, right: 0,
        textAlign: 'center', color: '#6b7280', fontSize: 11, fontWeight: 300
      }}>{label}</div>
    </div>
  );
}

// ===================================================================
// MAIN COMPONENT
// ===================================================================

export default function SafetyPop() {
  // ----- Config & session state -----
  const [config, setConfig] = useState({
    subject: 'TestSubject',
    sessionNum: 1,
    startTrial: 1,
    mode: 'fixed'
  });
  const [trialList, setTrialList] = useState([]);
  const [sessionState, setSessionState] = useState('idle'); // idle | running | paused | between | complete
  const [trialIdx, setTrialIdx] = useState(0);
  const [committed, setCommitted] = useState(false); // once a session starts, lock config

  // ----- Current trial state -----
  const [trial, setTrial] = useState(null);
  const [leftStims, setLeftStims] = useState([]);
  const [rightStims, setRightStims] = useState([]);
  const [bubbleTouches, setBubbleTouches] = useState(0);
  const [oddityWins, setOddityWins] = useState(0);
  const [oddityErrors, setOddityErrors] = useState(0);
  const [transitioning, setTransitioning] = useState(false);

  // ----- Data accumulation -----
  const [rows, setRows] = useState([]); // completed-trial rows
  const touchLogRef = useRef([]);
  const trialStartRef = useRef(0);
  const sessionStartRef = useRef(0);
  const firstTouchTaskRef = useRef('');
  const firstBubbleCellRef = useRef(-1);
  const oddTwoStimWinRef = useRef('NA');
  const latencyFirstTouchRef = useRef(-1);
  const latencyFirstTargetRef = useRef(-1);

  // ----- Build trial list when config changes -----
  useEffect(() => {
    let list;
    if (config.mode === 'fixed') {
      list = shuffleSeeded(CANONICAL_60, config.sessionNum * 12345);
    } else {
      list = shuffle(CANONICAL_60);
    }
    setTrialList(list);
  }, [config.sessionNum, config.mode]);

  // ----- Elapsed time tick -----
  const [tick, setTick] = useState(0);
  useEffect(() => {
    if (sessionState !== 'running' && sessionState !== 'between') return;
    const id = setInterval(() => setTick(t => t + 1), 250);
    return () => clearInterval(id);
  }, [sessionState]);

  // ----- Helpers -----
  const elapsedMs = () => sessionStartRef.current ? (Date.now() - sessionStartRef.current) : 0;
  const fmtTime = (ms) => {
    const s = Math.floor(ms / 1000);
    return `${Math.floor(s / 60)}m ${String(s % 60).padStart(2,'0')}s`;
  };

  // ----- Start a single trial -----
  const startTrial = useCallback((idx) => {
    if (idx >= trialList.length) {
      setSessionState('complete');
      return;
    }
    const parsed = parseTrialCode(trialList[idx]);
    const positions = generatePositions(parsed);
    const { leftStims: ls, rightStims: rs } = buildStims(parsed, positions);

    setTrial({ ...parsed, positions, leftPos: positions.leftPos, rightPos: positions.rightPos });
    setLeftStims(ls);
    setRightStims(rs);
    setBubbleTouches(0);
    setOddityWins(0);
    setOddityErrors(0);
    setTransitioning(false);

    touchLogRef.current = [];
    firstTouchTaskRef.current = '';
    firstBubbleCellRef.current = -1;
    oddTwoStimWinRef.current = 'NA';
    latencyFirstTouchRef.current = -1;
    latencyFirstTargetRef.current = -1;
    trialStartRef.current = Date.now();
  }, [trialList]);

  // ----- Start / Pause / Reset -----
  const handleStart = () => {
    if (sessionState === 'complete') return;
    if (sessionState === 'idle') {
      // First start: initialize from config
      sessionStartRef.current = Date.now();
      setCommitted(true);
      const startIdx = Math.max(0, (config.startTrial - 1));
      setTrialIdx(startIdx);
      setSessionState('running');
      startTrial(startIdx);
    } else if (sessionState === 'paused') {
      setSessionState('running');
      // Restart current trial fresh
      startTrial(trialIdx);
    }
  };

  const handlePause = () => {
    if (sessionState === 'running') setSessionState('paused');
  };

  const handleReset = () => {
    setSessionState('idle');
    setCommitted(false);
    setTrialIdx(0);
    setTrial(null);
    setLeftStims([]);
    setRightStims([]);
    setRows([]);
    setBubbleTouches(0);
    setOddityWins(0);
    setOddityErrors(0);
    sessionStartRef.current = 0;
    touchLogRef.current = [];
  };

  // ----- Record completed trial -----
  const recordTrial = (completedBy) => {
    if (!trial) return;
    const trialTime = Date.now() - trialStartRef.current;
    const oddSide = trial.leftTask === 'Oddity' ? 'L' : (trial.rightTask === 'Oddity' ? 'R' : '-');
    const targetSide = trial.type === 'F' ? 'B' : oddSide;
    const targetCellPos = trial.positions.targetCellIndex >= 0
      ? (oddSide === 'L' ? trial.positions.leftPos[trial.positions.targetCellIndex] : trial.positions.rightPos[trial.positions.targetCellIndex])
      : -1;

    // FirstBubbleGhost
    let firstBubbleGhost = 'NA';
    if (['A','B','C','D'].includes(trial.type)) {
      if (firstBubbleCellRef.current < 0) firstBubbleGhost = 3;
      else if (firstBubbleCellRef.current === targetCellPos) firstBubbleGhost = 1;
      else firstBubbleGhost = 2;
    }

    const row = {
      trial: trialIdx + 1,
      code: trial.code,
      type: trial.type,
      face: trial.face,
      side: trial.side,
      bubN: trial.bubN,
      oddN: trial.oddN,
      probe: trial.isProbe ? 'Y' : 'N',
      completedBy,
      bubTouches: bubbleTouches,
      oddWins: oddityWins,
      oddErrors: oddityErrors,
      oddTwoStimWin: oddTwoStimWinRef.current,
      firstBubbleGhost,
      targetCellPos,
      targetSide,
      latencyFirstTouch_ms: latencyFirstTouchRef.current,
      latencyFirstTarget_ms: latencyFirstTargetRef.current,
      trialTime_ms: trialTime,
      touchLog: [...touchLogRef.current],
      firstTouchTask: firstTouchTaskRef.current,
      leftPos: [...trial.positions.leftPos],
      rightPos: [...trial.positions.rightPos]
    };
    setRows(prev => [...prev, row]);

    // Transition to next trial
    setSessionState('between');
    setTimeout(() => {
      const next = trialIdx + 1;
      if (next >= trialList.length) {
        setSessionState('complete');
      } else {
        setTrialIdx(next);
        setSessionState('running');
        startTrial(next);
      }
    }, ITI);
  };

  // ----- Touch handler -----
  const handleTouch = (stim) => {
    if (sessionState !== 'running' || transitioning) return;
    const elapsed = Date.now() - trialStartRef.current;
    const sideStims = stim.side === 'L' ? leftStims : rightStims;
    const aliveCount = sideStims.filter(s => s.alive).length;

    // Latch latencies
    if (latencyFirstTouchRef.current < 0) latencyFirstTouchRef.current = elapsed;
    if (firstTouchTaskRef.current === '') {
      firstTouchTaskRef.current = stim.kind === 'Bubble' ? 'Bubble' : 'Oddity';
    }
    if (stim.kind === 'Target' && latencyFirstTargetRef.current < 0) {
      latencyFirstTargetRef.current = elapsed;
    }
    if (stim.kind === 'Bubble' && firstBubbleCellRef.current < 0) {
      firstBubbleCellRef.current = stim.cell;
    }

    // Touch log entry: elapsed,side,task,stimIdx,cellPos,stimTag,bubbleTouches,oddityWins
    const sideTask = stim.side === 'L' ? trial.leftTask : trial.rightTask;
    touchLogRef.current.push({
      ms: elapsed,
      side: stim.side,
      task: sideTask,
      idx: stim.idx,
      cell: stim.cell,
      tag: stim.kind,
      bubbleTouches: bubbleTouches,
      oddityWins: oddityWins
    });

    if (stim.kind === 'Bubble') {
      handleBubble(stim);
    } else if (stim.kind === 'Target') {
      // 2-stim win latch
      if (aliveCount === 2 && oddTwoStimWinRef.current === 'NA') {
        oddTwoStimWinRef.current = '1';
      }
      handleTarget(stim);
    } else if (stim.kind === 'Distractor') {
      // 2-stim loss latch
      if (aliveCount === 2 && oddTwoStimWinRef.current === 'NA') {
        oddTwoStimWinRef.current = '0';
      }
      handleDistractor(stim);
    }
  };

  // ----- Bubble pop -----
  const handleBubble = (stim) => {
    setBubbleTouches(prev => prev + 1);
    // Mark this stim dead
    const setSide = stim.side === 'L' ? setLeftStims : setRightStims;
    setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, alive: false, enabled: false } : s));

    // Check if this bubble side is now empty (the touched stim was alive in closure)
    const thisSide = stim.side === 'L' ? leftStims : rightStims;
    const aliveAfter = thisSide.filter(s => s.alive).length - 1;

    if (aliveAfter <= 0) {
      // For E trials, the side fully popped means trial complete.
      // For A-D/G/H bubble-side completion, same.
      setTimeout(() => recordTrial('Bubble'), 300);
    }
  };

  // ----- Target touch -----
  const handleTarget = (stim) => {
    setOddityWins(prev => prev + 1);

    const sideStims = stim.side === 'L' ? leftStims : rightStims;
    const aliveAfter = sideStims.filter(s => s.alive).length - 1;

    // For F trials, check completion on this side independently
    if (trial.type === 'F') {
      if (aliveAfter <= 0) {
        // Side complete
        const setSide = stim.side === 'L' ? setLeftStims : setRightStims;
        setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, alive: false } : s));
        setTimeout(() => recordTrial('Oddity'), 300);
        return;
      }
    }

    if (aliveAfter <= 0) {
      // Oddity side complete
      const setSide = stim.side === 'L' ? setLeftStims : setRightStims;
      setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, alive: false } : s));
      setTimeout(() => recordTrial('Oddity'), 300);
      return;
    }

    // Stage transition: brief vanish, then target migrates to a survivor cell
    setTransitioning(true);
    const setSide = stim.side === 'L' ? setLeftStims : setRightStims;
    setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, alive: false } : s));

    setTimeout(() => {
      setSide(prev => {
        const survivors = prev.filter(s => s.alive);
        if (survivors.length === 0) return prev;
        const newTargetCell = survivors[Math.floor(Math.random() * survivors.length)].cell;
        return prev.map(s => {
          if (!s.alive) return s;
          if (s.cell === newTargetCell) return { ...s, kind: 'Target', isTarget: true, enabled: true };
          return { ...s, kind: 'Distractor', isTarget: false, enabled: true };
        });
      });
      setTransitioning(false);
    }, STAGE_TRANSITION);
  };

  // ----- Distractor touch (timeout) -----
  const handleDistractor = (stim) => {
    setOddityErrors(prev => prev + 1);
    const setSide = stim.side === 'L' ? setLeftStims : setRightStims;
    setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, enabled: false } : s));
    setTimeout(() => {
      setSide(prev => prev.map((s, i) => i === stim.idx ? { ...s, enabled: true } : s));
    }, DISTRACTOR_TIMEOUT);
  };

  // ===============================================================
  // METRICS COMPUTATION
  // ===============================================================
  const metrics = (() => {
    const m = {
      trials: rows.length,
      bubbleTouches: 0,
      oddityTouches: 0,
      perType: { A:[], B:[], C:[], D:[] },
      perEmotion: { Angry:[], Happy:[], Fearful:[] },
      F4: [], F8: [],
      ghosts: { A:[0,0], B:[0,0], C:[0,0], D:[0,0] },  // [ghost, total bubble-attempts]
      bubComplete: { A:[0,0], B:[0,0], C:[0,0], D:[0,0] }, // [bubCompl, total]
      firstBub: { A:[0,0], B:[0,0], C:[0,0], D:[0,0] },
      oddTouches: { A:[0,0], B:[0,0], C:[0,0], D:[0,0] }, // [sum, n]
      latencyTarget: { Angry:[0,0], Happy:[0,0], Fearful:[0,0] }, // [sum, n]
      wavering: [0,0,0],  // [0 sw, 1 sw, 2+ sw]
      ooi: { A:[0,0], B:[0,0], C:[0,0], D:[0,0], overall:[0,0] }
    };
    for (const r of rows) {
      m.bubbleTouches += r.bubTouches;
      m.oddityTouches += r.oddWins + r.oddErrors;
      const t = r.type;
      // Per-type for A-D
      if (['A','B','C','D'].includes(t)) {
        m.perType[t].push(r);
        m.bubComplete[t][1] += 1;
        if (r.completedBy === 'Bubble') m.bubComplete[t][0] += 1;
        if (r.firstTouchTask === 'Bubble') m.firstBub[t][0] += 1;
        m.firstBub[t][1] += 1;
        // Ghost
        if (r.firstBubbleGhost === 1 || r.firstBubbleGhost === 2) {
          m.ghosts[t][1] += 1;
          if (r.firstBubbleGhost === 1) m.ghosts[t][0] += 1;
        }
        // Odd touches when completed by oddity
        if (r.completedBy === 'Oddity') {
          m.oddTouches[t][0] += r.oddWins + r.oddErrors;
          m.oddTouches[t][1] += 1;
        }
        // OOI: 0.5*bub_frac + 0.3*first_bub + 0.2*bub_complete
        const totalTouches = r.bubTouches + r.oddWins + r.oddErrors;
        const bubFrac = totalTouches > 0 ? r.bubTouches / totalTouches : 0;
        const firstBub = r.firstTouchTask === 'Bubble' ? 1 : 0;
        const bubCompl = r.completedBy === 'Bubble' ? 1 : 0;
        const ooi = 0.5*bubFrac + 0.3*firstBub + 0.2*bubCompl;
        m.ooi[t][0] += ooi; m.ooi[t][1] += 1;
        m.ooi.overall[0] += ooi; m.ooi.overall[1] += 1;
        // Per-emotion (combined A-D)
        if (r.face) {
          m.perEmotion[r.face]?.push(r);
        }
        // Wavering — count task switches in touch log
        let switches = 0, prev = null;
        for (const t2 of r.touchLog) {
          const cur = t2.tag === 'Bubble' ? 'B' : 'O';
          if (prev && cur !== prev) switches++;
          prev = cur;
        }
        if (switches === 0) m.wavering[0]++;
        else if (switches === 1) m.wavering[1]++;
        else m.wavering[2]++;
      }
      // F-trial sides
      if (t === 'F' && r.completedBy === 'Oddity') {
        // Determine completing side from touchLog
        let lT=0,lD=0,rT=0,rD=0;
        for (const e of r.touchLog) {
          if (e.task !== 'Oddity') continue;
          if (e.tag === 'Target') { if (e.side === 'L') lT++; else rT++; }
          else if (e.tag === 'Distractor') { if (e.side === 'L') lD++; else rD++; }
        }
        const leftLen = r.leftPos?.length || 0;
        const rightLen = r.rightPos?.length || 0;
        if (lT === leftLen && leftLen > 0) {
          (leftLen === 4 ? m.F4 : m.F8).push(lT + lD);
        } else if (rT === rightLen && rightLen > 0) {
          (rightLen === 4 ? m.F4 : m.F8).push(rT + rD);
        }
      }
      // Latency to target by emotion
      if (r.face && r.latencyFirstTarget_ms > 0) {
        m.latencyTarget[r.face][0] += r.latencyFirstTarget_ms;
        m.latencyTarget[r.face][1] += 1;
      }
    }
    return m;
  })();

  // ===============================================================
  // RENDER
  // ===============================================================

  const cellSize = 90;
  const gridW = 3 * cellSize;
  const gridH = 4 * cellSize;
  const taskW = gridW * 2 + 60;
  const taskH = gridH + 60;

  const stat = (n, d, dp = 0) => d === 0 ? '—' : `${(100*n/d).toFixed(dp)}%`;
  const mean = (sum, n, dp = 1) => n === 0 ? '—' : (sum / n).toFixed(dp);

  return (
    <div style={{
      fontFamily: '"IBM Plex Sans", -apple-system, BlinkMacSystemFont, sans-serif',
      background: '#0a0e14',
      color: '#e5e7eb',
      minHeight: '100vh',
      padding: 20
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
        .mono { font-family: 'JetBrains Mono', monospace; }
        .glow { box-shadow: 0 0 0 1px rgba(125,211,252,0.3), 0 0 24px rgba(125,211,252,0.15); }
        button { font-family: inherit; }
        button:disabled { opacity: 0.35; cursor: not-allowed; }
      `}</style>

      <div style={{ maxWidth: 1200, margin: '0 auto' }}>

        {/* HEADER */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 18 }}>
          <h1 style={{ fontSize: 22, fontWeight: 300, margin: 0, color: '#f0f9ff', letterSpacing: '-0.01em' }}>
            SafetyPop
          </h1>
          <span style={{ fontSize: 11, color: '#64748b', fontWeight: 400 }}>
            React demo · multi-touch opt-out paradigm
          </span>
          <span style={{ marginLeft: 'auto', fontSize: 11, color: sessionState === 'running' ? '#86efac' : sessionState === 'complete' ? '#fde68a' : '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
            {sessionState === 'running' && <Activity size={11} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 6 }} />}
            {sessionState}
          </span>
        </div>

        {/* CONTROLS */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(5, 1fr) auto',
          gap: 14,
          padding: 16,
          background: 'rgba(255,255,255,0.025)',
          borderRadius: 8,
          border: '1px solid rgba(255,255,255,0.05)',
          marginBottom: 18,
          alignItems: 'end'
        }}>
          <Field label="Subject">
            <input
              value={config.subject}
              onChange={(e) => !committed && setConfig({ ...config, subject: e.target.value })}
              disabled={committed}
              style={inputStyle}
            />
          </Field>
          <Field label="Session">
            <select
              value={config.sessionNum}
              onChange={(e) => !committed && setConfig({ ...config, sessionNum: +e.target.value })}
              disabled={committed}
              style={inputStyle}
            >
              {Array.from({length: 10}, (_,i) => i+1).map(n =>
                <option key={n} value={n}>{n}</option>
              )}
            </select>
          </Field>
          <Field label="Start trial">
            <select
              value={config.startTrial}
              onChange={(e) => !committed && setConfig({ ...config, startTrial: +e.target.value })}
              disabled={committed}
              style={inputStyle}
            >
              {Array.from({length: 60}, (_,i) => i+1).map(n =>
                <option key={n} value={n}>{n}</option>
              )}
            </select>
          </Field>
          <Field label="Mode">
            <select
              value={config.mode}
              onChange={(e) => !committed && setConfig({ ...config, mode: e.target.value })}
              disabled={committed}
              style={inputStyle}
            >
              <option value="fixed">Fixed sequence</option>
              <option value="random">Random shuffle</option>
            </select>
          </Field>
          <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.4 }}>
            <div>Trial: <span className="mono" style={{ color: '#e5e7eb' }}>{rows.length} / {trialList.length}</span></div>
            <div>Elapsed: <span className="mono" style={{ color: '#e5e7eb' }}>{fmtTime(elapsedMs())}</span></div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={handleStart}
              disabled={sessionState === 'running' || sessionState === 'complete'}
              style={{ ...btnStyle, background: '#0891b2', color: '#fff' }}
            >
              <Play size={14} />
              {sessionState === 'paused' ? 'Resume' : 'Start'}
            </button>
            <button
              onClick={handlePause}
              disabled={sessionState !== 'running'}
              style={{ ...btnStyle, background: '#475569' }}
            >
              <Pause size={14} />
              Pause
            </button>
            <button
              onClick={handleReset}
              style={{ ...btnStyle, background: '#7f1d1d' }}
            >
              <RotateCcw size={14} />
              Reset
            </button>
          </div>
        </div>

        {/* TRIAL INFO STRIP */}
        {trial && sessionState !== 'idle' && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(6, 1fr)',
            gap: 18,
            padding: '10px 16px',
            background: 'rgba(255,255,255,0.015)',
            borderRadius: 6,
            border: '1px solid rgba(255,255,255,0.04)',
            marginBottom: 12,
            fontSize: 11
          }}>
            <InfoStat label="Code" value={trial.code} />
            <InfoStat label="Type" value={`${trial.type} (${trial.bubN}b / ${trial.oddN}o)`} />
            <InfoStat label="Face" value={trial.face ? `${FACE_EMOJI[trial.face]} ${trial.face}${trial.isProbe ? ' [PROBE]' : ''}` : '—'} />
            <InfoStat label="Bub touches" value={`${bubbleTouches} / ${trial.bubN}`} />
            <InfoStat label="Odd wins" value={`${oddityWins} / ${trial.oddN}`} />
            <InfoStat label="Odd errs" value={oddityErrors} />
          </div>
        )}

        {/* TASK SCREEN */}
        <div style={{
          position: 'relative',
          width: taskW,
          height: taskH + 30,
          margin: '0 auto 18px',
          background: 'radial-gradient(ellipse at center, #1a1f2e 0%, #0a0e14 80%)',
          borderRadius: 12,
          border: '1px solid rgba(255,255,255,0.06)',
          padding: 30,
          boxSizing: 'border-box'
        }}>
          {sessionState === 'idle' && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              color: '#64748b', fontSize: 13, fontWeight: 300
            }}>
              Configure parameters above and press Start
            </div>
          )}
          {sessionState === 'paused' && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              color: '#fde68a', fontSize: 14, fontWeight: 400,
              background: 'rgba(0,0,0,0.7)', zIndex: 50
            }}>
              Paused — press Resume to restart current trial
            </div>
          )}
          {sessionState === 'complete' && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              color: '#86efac', fontSize: 18, fontWeight: 400, gap: 10
            }}>
              <div>Session complete</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>
                {rows.length} trials in {fmtTime(elapsedMs())}
              </div>
            </div>
          )}
          {sessionState === 'between' && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              color: '#64748b', fontSize: 12, fontStyle: 'italic',
              zIndex: 50
            }}>
              ...
            </div>
          )}

          {(sessionState === 'running' || sessionState === 'between') && trial && (
            <div style={{
              display: 'flex',
              gap: 60,
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%'
            }}>
              <TaskGrid stims={leftStims} onTouch={handleTouch} cellSize={cellSize}
                label="Left" disabled={transitioning || sessionState !== 'running'} />
              <TaskGrid stims={rightStims} onTouch={handleTouch} cellSize={cellSize}
                label="Right" disabled={transitioning || sessionState !== 'running'} />
            </div>
          )}
        </div>

        {/* METRICS */}
        <div style={{
          padding: 16,
          background: 'rgba(255,255,255,0.025)',
          borderRadius: 8,
          border: '1px solid rgba(255,255,255,0.05)',
          fontSize: 11
        }}>
          <div style={{ fontSize: 10, fontWeight: 500, color: '#94a3b8', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 10 }}>
            Live Metrics
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>

            {/* LEFT COLUMN — opt-out & performance */}
            <div className="mono" style={{ fontSize: 11, lineHeight: 1.6 }}>
              <div style={{ color: '#7dd3fc', marginBottom: 4 }}>Opt-out &amp; performance (A-D)</div>
              <div style={{ color: '#64748b', fontSize: 10 }}>
                Type      BubCompl  FirstBub   Ghost    OddTouches
              </div>
              {['A','B','C','D'].map(t => {
                const bc = metrics.bubComplete[t];
                const fb = metrics.firstBub[t];
                const gh = metrics.ghosts[t];
                const ot = metrics.oddTouches[t];
                const opt = ['A','B'].includes(t) ? 4 : 8;
                const desc = { A:'(4/4)', B:'(8/4)', C:'(4/8)', D:'(8/8)' }[t];
                return (
                  <div key={t} style={{ color: '#cbd5e1' }}>
                    {`${t} ${desc.padEnd(7)} ${stat(bc[0],bc[1]).padStart(7)}  ${stat(fb[0],fb[1]).padStart(7)}  ${stat(gh[0],gh[1]).padStart(6)}   ${mean(ot[0],ot[1])} / ${opt}`}
                  </div>
                );
              })}
              <div style={{ color: '#cbd5e1' }}>
                {`F (forced)         4-side: ${mean(metrics.F4.reduce((a,b)=>a+b,0), metrics.F4.length)} / 4 (n=${metrics.F4.length})   8-side: ${mean(metrics.F8.reduce((a,b)=>a+b,0), metrics.F8.length)} / 8 (n=${metrics.F8.length})`}
              </div>

              <div style={{ marginTop: 14, color: '#7dd3fc' }}>Cumulative OOI</div>
              <div style={{ color: '#cbd5e1' }}>
                Overall: {metrics.ooi.overall[1] === 0 ? '—' : (metrics.ooi.overall[0] / metrics.ooi.overall[1]).toFixed(2)}
                {' '}A: {metrics.ooi.A[1] === 0 ? '—' : (metrics.ooi.A[0] / metrics.ooi.A[1]).toFixed(2)}
                {' '}B: {metrics.ooi.B[1] === 0 ? '—' : (metrics.ooi.B[0] / metrics.ooi.B[1]).toFixed(2)}
                {' '}C: {metrics.ooi.C[1] === 0 ? '—' : (metrics.ooi.C[0] / metrics.ooi.C[1]).toFixed(2)}
                {' '}D: {metrics.ooi.D[1] === 0 ? '—' : (metrics.ooi.D[0] / metrics.ooi.D[1]).toFixed(2)}
              </div>
            </div>

            {/* RIGHT COLUMN — emotion & wavering */}
            <div className="mono" style={{ fontSize: 11, lineHeight: 1.6 }}>
              <div style={{ color: '#fde68a', marginBottom: 4 }}>Latency to target (by emotion)</div>
              {['Angry','Happy','Fearful'].map(e => {
                const [sum, n] = metrics.latencyTarget[e];
                return (
                  <div key={e} style={{ color: '#cbd5e1' }}>
                    {`${e.padEnd(8)}  ${n === 0 ? '—' : (sum/n/1000).toFixed(2) + 's'} (n=${n})`}
                  </div>
                );
              })}

              <div style={{ marginTop: 14, color: '#fde68a' }}>Wavering (A-D)</div>
              {(() => {
                const sum = metrics.wavering.reduce((a,b)=>a+b,0);
                return (
                  <div style={{ color: '#cbd5e1' }}>
                    0 sw: {stat(metrics.wavering[0], sum)}
                    {'  '}1 sw: {stat(metrics.wavering[1], sum)}
                    {'  '}2+: {stat(metrics.wavering[2], sum)}
                  </div>
                );
              })()}

              <div style={{ marginTop: 14, color: '#fde68a' }}>Session totals</div>
              <div style={{ color: '#cbd5e1' }}>
                Bubble touches: {metrics.bubbleTouches}{'   '}Oddity touches: {metrics.oddityTouches}
              </div>
              <div style={{ color: '#cbd5e1' }}>
                Trials complete: {rows.length}
              </div>
            </div>
          </div>
        </div>

        {/* CREDIT */}
        <div style={{
          textAlign: 'center', marginTop: 20, fontSize: 10, color: '#475569', fontWeight: 300
        }}>
          SafetyPop demo · faithful port of WPF/VB chimp version · interact with the stim grid above
        </div>
      </div>
    </div>
  );
}

// ===================================================================
// SMALL HELPER COMPONENTS / STYLES
// ===================================================================

function Field({ label, children }) {
  return (
    <div>
      <div style={{
        fontSize: 9, color: '#94a3b8', textTransform: 'uppercase',
        letterSpacing: '0.1em', marginBottom: 4, fontWeight: 500
      }}>{label}</div>
      {children}
    </div>
  );
}

function InfoStat({ label, value }) {
  return (
    <div>
      <div style={{ color: '#64748b', fontSize: 9, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
      <div className="mono" style={{ color: '#e5e7eb', fontSize: 12, marginTop: 2 }}>{value}</div>
    </div>
  );
}

const inputStyle = {
  width: '100%',
  background: 'rgba(0,0,0,0.4)',
  color: '#e5e7eb',
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: 4,
  padding: '6px 8px',
  fontSize: 12,
  fontFamily: 'inherit'
};

const btnStyle = {
  display: 'flex', alignItems: 'center', gap: 6,
  padding: '8px 14px',
  fontSize: 12,
  fontWeight: 500,
  border: 'none',
  borderRadius: 5,
  color: '#fff',
  cursor: 'pointer',
  letterSpacing: '0.02em'
};
