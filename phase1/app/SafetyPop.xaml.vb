Imports System.Windows.Media.Animation
Imports System.Windows.Shapes
Imports System.Windows.Controls
Imports System.Windows.Input
Imports System.Media
Imports System.Linq

Class SafetyPop

    ' ============================================
    ' SESSION INFO (matches ApeTouch pattern)
    ' ============================================
    Dim subjectName As String = "TestSubject"
    Dim speciesName As String = "-"
    Dim sessionNumber As String = "1"
    Dim locationName As String = "Orang1"
    Dim mydate As Date = Now
    Dim datestring As String = ""
    Dim mytimestring As String = ""

    ' ============================================
    ' TRIAL MANAGEMENT
    ' ============================================
    Dim sessionTrials() As String
    Dim currentTrial As Integer = 0
    Dim trialActive As Boolean = False

    ' Has the operator pressed play to initialize the session yet?
    ' When False, the task is in the initial paused/black state and the
    ' first play press configures the run from radio buttons + dropdowns.
    ' When True, the session is locked in and play/pause toggles run state.
    Dim sessionInitialized As Boolean = False

    ' Twenty pre-generated fixed sequences for Mode 2 (resume-able).
    ' Generated once in Window_Loaded by seeded shuffle of canonical60Codes
    ' so they're stable across runs.
    Dim fixedSequences(19)() As String

    ' Canonical 60-trial composition used by both run modes. Mode 1 shuffles
    ' this freshly each play press; Mode 2 builds 20 deterministic shuffles
    ' from it. Codes are {Type}{FaceCode}{Side}, see ParseTrialCode for
    ' decoding. Composition: 24 core A-D, 6 A-probes, 6 I-probes, 2 E,
    ' 6 F, 2 G, 2 H, 6 I-std, 6 J = 60 trials.
    Dim canonical60Codes As String() = {
        "A1L", "A1R", "A2L", "A2R", "A3L", "A3R",
        "A4L", "A4R", "A5L", "A5R", "A6L", "A6R",
        "B1L", "B1R", "B2L", "B2R", "B3L", "B3R",
        "C1L", "C1R", "C2L", "C2R", "C3L", "C3R",
        "D1L", "D1R", "D2L", "D2R", "D3L", "D3R",
        "E0L", "E0R",
        "F1L", "F1R", "F2L", "F2R", "F3L", "F3R",
        "G0L", "G0R",
        "H0L", "H0R",
        "I1L", "I1R", "I2L", "I2R", "I3L", "I3R",
        "I4L", "I4R", "I5L", "I5R", "I6L", "I6R",
        "J1L", "J1R", "J2L", "J2R", "J3L", "J3R"
    }

    Dim trialType As String = ""
    Dim faceCode As String = ""
    Dim sideCode As String = ""
    Dim bubbleCount As Integer = 0
    Dim oddityCount As Integer = 0
    Dim leftTask As String = ""
    Dim rightTask As String = ""
    Dim targetFace As String = ""
    Dim completedBy As String = ""
    Dim isProbe As Boolean = False
    Dim distractorType As String = ""  ' "Neutral" or "Inverted"

    ' ============================================
    ' GRID POSITION MANAGEMENT
    ' ============================================
    Dim leftPositions As New List(Of Integer)
    Dim rightPositions As New List(Of Integer)
    Dim targetCellIndex As Integer = -1

    ' ============================================
    ' BUBBLE STATE
    ' ============================================
    Dim bubbleTouchCount As Integer = 0
    Dim bubbleTotal As Integer = 0

    ' ============================================
    ' ODDITY STATE
    ' ============================================
    Dim oddityWinCount As Integer = 0
    Dim oddityErrorCount As Integer = 0
    Dim oddityTotal As Integer = 0
    Dim oddityRemaining As Integer = 0
    Dim oddityTargetRectIndex As Integer = -1

    ' First-encountered 2-stim choice in the trial:
    '   "NA" = subject never made a 2-stim choice (didn't reach 2-stim stage,
    '          or completed trial via bubbles before getting there)
    '   "1"  = first touch at 2-stim stage was target (correct)
    '   "0"  = first touch at 2-stim stage was distractor (incorrect)
    ' For F-trials (both sides oddity), records whichever side hit 2-stim
    ' first. Only the FIRST 2-stim touch is recorded; subsequent touches
    ' at the same or another 2-stim stage do not overwrite.
    Dim oddTwoStimWin As String = "NA"

    ' cellPos (1-12) of the FIRST bubble touched in the trial.
    ' -1 means no bubble was touched. Used to compute FirstBubbleGhost
    ' in RecordTrialData: if this matches the oddity target's cellPos,
    ' the subject's first bubble pop was the ghost-target bubble.
    Dim firstBubbleCellPos As Integer = -1

    ' Task of the first touch in the trial (Bubble/Oddity), latched in
    ' StimTouched. Used for OOI computation in metrics aggregation.
    Dim firstTouchTask As String = ""

    ' Latency (ms from trial start) to first touch of any kind in the trial.
    ' -1 means no touch occurred during the trial.
    Dim latencyFirstTouch As Long = -1

    ' Latency (ms from trial start) to first correct oddity target touch.
    ' -1 means no target was ever touched (bubble-completed, or no oddity).
    Dim latencyFirstTarget As Long = -1

    ' ============================================
    ' LIVE METRICS AGGREGATORS
    ' Reset at session init, updated after each completed trial.
    ' Index 0-3 = trial types A/B/C/D. Index 0-2 = emotions Angry/Happy/Fearful.
    ' ============================================
    Dim sessionStartTime As DateTime
    Dim trialTimes As New List(Of Long)

    ' Save-state tracking: True if the current data stream / metrics state
    ' has been saved since the last data-generating event. Reset to False
    ' every time a new trial completes; set to True on successful save.
    ' Both start True because there's nothing to save before any trial.
    Dim dataStreamSaved As Boolean = True
    Dim metricsSaved As Boolean = True

    ' Session-cumulative touch counts (all trial types, all completed trials)
    Dim mt_sessionBubbleTouches As Integer = 0
    Dim mt_sessionOddityTouches As Integer = 0  ' wins + errors

    ' Per-trial-type (A,B,C,D)
    Dim mt_trialsByType(3) As Integer
    Dim mt_bubCompleteByType(3) As Integer
    Dim mt_firstTouchBubByType(3) As Integer
    Dim mt_ghostFirstByType(3) As Integer
    Dim mt_bubAttemptByType(3) As Integer   ' trials where any bubble was touched
    Dim mt_switchesByType(3) As Integer
    Dim mt_zeroSwitchByType(3) As Integer
    Dim mt_oneSwitchByType(3) As Integer
    Dim mt_twoPlusSwitchByType(3) As Integer
    Dim mt_ooiSumByType(3) As Double

    ' Per-emotion (Angry=0, Happy=1, Fearful=2) within A-D combined
    Dim mt_trialsByEmotionAD(2) As Integer
    Dim mt_bubCompleteByEmotionAD(2) As Integer
    Dim mt_firstTouchBubByEmotionAD(2) As Integer
    Dim mt_ghostFirstByEmotionAD(2) As Integer
    Dim mt_bubAttemptByEmotionAD(2) As Integer

    ' Oddity error rates per emotion: chose context (A-D, completedBy=Oddity)
    ' vs forced context (I, J). "ErrorTouches" = distractor touches at 3+ stim
    ' stage; "CorrectTouches" = target touches at 3+ stim stage. 2-stim stage
    ' is tracked separately.
    Dim mt_chose_preTwoErr(2) As Integer
    Dim mt_chose_preTwoCorrect(2) As Integer
    Dim mt_forced_preTwoErr(2) As Integer
    Dim mt_forced_preTwoCorrect(2) As Integer

    ' 2-stim choice outcomes per emotion: chose vs forced
    Dim mt_chose_twoStimWin(2) As Integer
    Dim mt_chose_twoStimLoss(2) As Integer
    Dim mt_forced_twoStimWin(2) As Integer
    Dim mt_forced_twoStimLoss(2) As Integer

    ' Per-emotion latency to first oddity target touch (ms), summed for
    ' mean computation. Counted across all trial types with an emotion
    ' target and at least one target touch (A-D chose-oddity, F, I, J).
    Dim mt_targetLatencySum(2) As Long
    Dim mt_targetLatencyCount(2) As Integer

    ' Oddity-completion performance per trial type (A,B,C,D): on trials
    ' where the subject chose oddity and completed it, sum of total
    ' touches required (OddWins + OddErrors). Mean reveals skill —
    ' compare to OddN (4 for A,B; 8 for C,D) as the optimum.
    Dim mt_oddCompleteTouchesByType(3) As Integer
    Dim mt_oddCompleteTrialsByType(3) As Integer

    ' F-trial performance (oddity vs oddity, no bubble option).
    ' On F trials, subject completes either the 4-stim or 8-stim side.
    ' Track total touches on completing side, separately for each side size.
    Dim mt_F_4side_TouchesSum As Integer = 0
    Dim mt_F_4side_Count As Integer = 0
    Dim mt_F_8side_TouchesSum As Integer = 0
    Dim mt_F_8side_Count As Integer = 0

    ' F-trial mirroring: track target rect index on each side independently
    Dim fTypeRightTargetIndex As Integer = -1
    Dim leftOddityTargetIdx As Integer = -1
    Dim rightOddityTargetIdx As Integer = -1
    ' F-trial: predetermined sequence of cells the target visits during elimination
    ' Both sides follow the same path independently
    Dim fTargetPath As New List(Of Integer)
    Dim fTargetPathStep As New Dictionary(Of String, Integer)  ' "L" or "R" -> current step

    ' ============================================
    ' RECTANGLE ARRAYS AND STATE
    ' ============================================
    Dim leftRects(7) As Rectangle
    Dim rightRects(7) As Rectangle
    Dim leftAlive(7) As Boolean
    Dim rightAlive(7) As Boolean

    ' ============================================
    ' TOUCH LOG AND TIMING
    ' ============================================
    Dim touchLog As New List(Of String)
    Dim trialStopwatch As New Stopwatch

    ' ============================================
    ' SOUNDS
    ' ============================================
    Dim bubbleSound As New System.Media.SoundPlayer("Stim/Bubble.wav")
    Dim clickSound As New System.Media.SoundPlayer("Stim/Click.wav")
    Dim popSound As New System.Media.SoundPlayer("Stim/boop1.wav")
    Dim dingSound As New System.Media.SoundPlayer("Stim/DingDing.wav")
    Dim silenceSound As New System.Media.SoundPlayer("Stim/silence.wav")

    ' ============================================
    ' SHARED RNG (Fisher-Yates)
    ' ============================================
    Private Shared Rng As New Random()


    ' ============================================
    ' KEYBOARD HANDLER (D = toggle curtain, Esc = home)
    ' ============================================
    Private Sub Window_KeyDown(sender As Object, e As KeyEventArgs) Handles MyBase.KeyDown
        ' D = toggle curtain (pause/resume ape screen visual)
        If e.Key = Key.D Then
            If Curtain.Visibility = Visibility.Visible Then
                Curtain.Visibility = Visibility.Hidden
            Else
                Curtain.Visibility = Visibility.Visible
            End If
        End If
        ' Escape = return to ApeTouch menu
        If e.Key = Key.Escape Then
            gohome()
        End If
    End Sub


    ' ============================================
    ' PAGE UNLOADED (ApeTouch lifecycle cleanup)
    ' ============================================
    Private Sub window_unloading() Handles MyBase.Unloaded
        trialActive = False
        Application.Current.Properties("gflag") = False
        Application.Current.Properties("T1flag") = False
        Application.Current.Properties("T2flag") = False
        Application.Current.Properties("T3flag") = False
        Application.Current.Properties("T4flag") = False
        Application.Current.Properties("T5flag") = False
        Application.Current.Properties("T6flag") = False
        My.Settings.Pelletgo = False
        My.Settings.Save()
        Mouse.OverrideCursor = Cursors.Arrow
    End Sub


    ' ============================================
    ' PAGE LOADED
    ' ============================================
    Private Sub Window_Loaded(sender As Object, e As System.Windows.RoutedEventArgs) Handles MyBase.Loaded

        ' --- ApeTouch lifecycle hooks (drives MainWindow grandtimer) ---
        Application.Current.Properties("gflag") = True
        Select Case CurrentQuePosition
            Case 1 : Application.Current.Properties("T1flag") = True
            Case 2 : Application.Current.Properties("T2flag") = True
            Case 3 : Application.Current.Properties("T3flag") = True
            Case 4 : Application.Current.Properties("T4flag") = True
            Case 5 : Application.Current.Properties("T5flag") = True
            Case 6 : Application.Current.Properties("T6flag") = True
        End Select

        ' Pull the participant from the ApeTouch global if it's been set
        If Not String.IsNullOrEmpty(selectedparticipant) Then
            subjectName = selectedparticipant
        End If

        ' Bind the subject dropdown to the ApeTouch participant list and
        ' pre-select the currently-active participant. Operator can change
        ' the selection before pressing play; the selection is committed
        ' (and the ComboBox disabled) when the session starts.
        subject.DataContext = participantlist
        subject.Text = selectedparticipant

        ' Make sure this Page receives keyboard input
        Me.Focusable = True
        Me.Focus()

        silenceSound.Play()
        bubbleSound.LoadAsync()
        clickSound.LoadAsync()
        popSound.LoadAsync()
        dingSound.LoadAsync()

        ' Session info
        mydate = Now
        datestring = mydate.ToString("MM-dd-yyyy")
        mytimestring = mydate.ToString("HH:mm:ss")
        lbl_Subject.Content = subjectName
        lbl_Species.Content = speciesName
        lbl_DateTimeString.Content = datestring
        lbl_Session.Content = sessionNumber
        lbl_SessionStart.Content = mytimestring
        lbl_Location.Content = locationName
        lbldbsubject.Content = subjectName
        lbldbtimestring.Content = datestring & " " & mytimestring
        lbl_StatusIndicator.Content = "RUNNING"

        ' Map XAML rectangles into arrays
        leftRects(0) = L1 : leftRects(1) = L2 : leftRects(2) = L3 : leftRects(3) = L4
        leftRects(4) = L5 : leftRects(5) = L6 : leftRects(6) = L7 : leftRects(7) = L8
        rightRects(0) = R1 : rightRects(1) = R2 : rightRects(2) = R3 : rightRects(3) = R4
        rightRects(4) = R5 : rightRects(5) = R6 : rightRects(6) = R7 : rightRects(7) = R8

        ' Attach touch handler on MouseDown only. A stim registers only when
        ' it is pressed/tapped directly; sliding or dragging a finger across a
        ' stim (which fires MouseEnter via WPF's touch-to-mouse promotion) no
        ' longer counts as a touch. The IsEnabled gating in StimTouched plus
        ' the per-stim disable-after-touch logic still act as the debounce.
        For Each r In leftRects
            AddHandler r.MouseDown, AddressOf StimTouched
        Next
        For Each r In rightRects
            AddHandler r.MouseDown, AddressOf StimTouched
        Next

        ' Set up grid row/column definitions
        SetupGrid(LeftGrid)
        SetupGrid(RightGrid)

        ' Hide all rects initially
        For Each r In leftRects : r.Visibility = Visibility.Hidden : Next
        For Each r In rightRects : r.Visibility = Visibility.Hidden : Next

        ' Generate the 20 fixed sequences via seeded shuffle of canonical60Codes.
        ' Each session's seed = sessionNum * 12345 so sequences are stable across
        ' runs but distinct from each other. Mode 2 picks one of these.
        For s As Integer = 1 To 20
            fixedSequences(s - 1) = GenerateSeededSequence(s * 12345)
        Next

        ' Populate session-number dropdown (1-20)
        For s As Integer = 1 To 20
            cmbSessionNumber.Items.Add(s.ToString())
        Next
        cmbSessionNumber.SelectedIndex = 0  ' default to session 1

        ' Populate starting-trial dropdown (1-60)
        For t As Integer = 1 To 60
            cmbStartTrial.Items.Add(t.ToString())
        Next
        cmbStartTrial.SelectedIndex = 0  ' default to trial 1

        ' Wire radio buttons to enable/disable starting-trial dropdown
        ' (random mode can't resume mid-session, so the dropdown is grayed out)
        AddHandler rbModeFixed.Checked, AddressOf RunMode_Changed
        AddHandler rbModeRandom.Checked, AddressOf RunMode_Changed
        UpdateModeDropdownStates()

        ' Miniview: live mirror of ape screen
        miniview1.Fill = New System.Windows.Media.VisualBrush(TaskScreen)

        ' Initial state: paused, curtain visible, play icon showing.
        ' First press of play will initialize the session from current
        ' radio + dropdown selections.
        PlayIcon.Visibility = Visibility.Visible
        PauseIcon.Visibility = Visibility.Hidden
        lbl_StatusIndicator.Content = "READY"
        Curtain.Visibility = Visibility.Visible

        ' Data header (CSV, ApeTouch convention: comma-space delimited)
        DataBox.Text = "Subject , Species , Date , Session , Location , " &
                        "Trial , Code , Type , Face , Side , LTask , RTask , " &
                        "BubN , OddN , TargetCellPos , TargetSide , LeftPositions , RightPositions , " &
                        "Probe , DistractorType , CompletedBy , " &
                        "BubTouches , OddWins , OddErrors , OddTwoStimWin , FirstBubbleGhost , " &
                        "LatencyFirstTouch_ms , LatencyFirstTarget_ms , TrialTime_ms , " &
                        "TouchLog" & vbCrLf

    End Sub


    Private Sub SetupGrid(grid As System.Windows.Controls.Grid)
        For i = 1 To 4
            Dim r As New RowDefinition()
            r.Height = New System.Windows.GridLength(160)
            grid.RowDefinitions.Add(r)
        Next
        For k = 1 To 3
            Dim c As New ColumnDefinition()
            c.Width = New System.Windows.GridLength(160)
            grid.ColumnDefinitions.Add(c)
        Next
    End Sub


    ' ============================================
    ' TRIAL SETUP
    ' ============================================
    Private Sub StartTrial()

        If currentTrial >= sessionTrials.Length Then
            EndSession()
            Exit Sub
        End If

        ParseTrialCode(sessionTrials(currentTrial))

        ' Reset all rectangles
        For i = 0 To 7
            ResetStim(leftRects(i))
            ResetStim(rightRects(i))
            leftAlive(i) = False
            rightAlive(i) = False
        Next

        GeneratePositions()

        ' Reset counters
        bubbleTouchCount = 0
        bubbleTotal = bubbleCount
        oddityWinCount = 0
        oddityErrorCount = 0
        oddityTotal = oddityCount
        oddityRemaining = oddityCount
        oddityTargetRectIndex = -1
        oddTwoStimWin = "NA"
        firstBubbleCellPos = -1
        firstTouchTask = ""
        latencyFirstTouch = -1
        latencyFirstTarget = -1
        touchLog.Clear()

        ' Place stimuli
        leftOddityTargetIdx = -1
        rightOddityTargetIdx = -1

        If trialType = "E" Then
            ' 4 vs 8 bubbles
            PlaceBubblesOnSide(leftRects, leftPositions, LeftGrid, leftAlive)
            PlaceBubblesOnSide(rightRects, rightPositions, RightGrid, rightAlive)

        ElseIf trialType = "F" Then
            ' 4 vs 8 oddity: both sides get oddity, target in same cell
            ' Left side: targetCellIndex is the target index within leftPositions
            PlaceOddityOnSide(leftRects, leftPositions, LeftGrid, leftAlive, True)
            leftOddityTargetIdx = oddityTargetRectIndex

            ' Right side: use fTypeRightTargetIndex
            Dim savedTargetCell As Integer = targetCellIndex
            targetCellIndex = fTypeRightTargetIndex
            PlaceOddityOnSide(rightRects, rightPositions, RightGrid, rightAlive, True)
            rightOddityTargetIdx = oddityTargetRectIndex
            targetCellIndex = savedTargetCell

        Else
            ' Standard A-D, G-J, probes
            If leftTask = "Bubble" Then PlaceBubblesOnSide(leftRects, leftPositions, LeftGrid, leftAlive)
            If rightTask = "Bubble" Then PlaceBubblesOnSide(rightRects, rightPositions, RightGrid, rightAlive)
            If leftTask = "Oddity" Then PlaceOddityOnSide(leftRects, leftPositions, LeftGrid, leftAlive, True)
            If rightTask = "Oddity" Then PlaceOddityOnSide(rightRects, rightPositions, RightGrid, rightAlive, leftTask <> "Oddity")
        End If

        ' Update control panel labels
        lblTrial.Content = (currentTrial + 1) & " / " & sessionTrials.Length
        lblTrialCode.Content = sessionTrials(currentTrial)
        lblTrialType.Content = trialType
        lblLeftTask.Content = leftTask
        lblRightTask.Content = rightTask
        lblBubbleCount.Content = bubbleCount
        lblOddityCount.Content = oddityCount
        lblOddityWins.Content = "0"
        lblOddityErrors.Content = "0"
        lblBubbleTouches.Content = "0"
        lblFace.Content = targetFace & If(isProbe, " [PROBE]", "")
        lblCompletedBy.Content = "-"
        lblTrialTime.Content = "-"

        ' Start clocks
        trialStopwatch.Restart()

        ' Animate in
        For i = 0 To 7
            If leftAlive(i) Then ReviveStim(leftRects(i))
            If rightAlive(i) Then ReviveStim(rightRects(i))
        Next

        trialActive = True

    End Sub


    ' ============================================
    ' PARSE TRIAL CODE
    ' ============================================
    Private Sub ParseTrialCode(code As String)

        trialType = Mid(code, 1, 1)
        faceCode = Mid(code, 2, 1)
        sideCode = Mid(code, 3, 1)

        Select Case trialType
            Case "A" : bubbleCount = 4 : oddityCount = 4
            Case "B" : bubbleCount = 8 : oddityCount = 4
            Case "C" : bubbleCount = 4 : oddityCount = 8
            Case "D" : bubbleCount = 8 : oddityCount = 8
            Case "E" : bubbleCount = 0 : oddityCount = 0  ' Special: 4 vs 8 bubbles
            Case "F" : bubbleCount = 0 : oddityCount = 0  ' Special: 4 vs 8 oddity
            Case "G" : bubbleCount = 4 : oddityCount = 0
            Case "H" : bubbleCount = 8 : oddityCount = 0
            Case "I" : bubbleCount = 0 : oddityCount = 4
            Case "J" : bubbleCount = 0 : oddityCount = 8
        End Select

        Select Case trialType
            Case "A", "B", "C", "D"
                If sideCode = "R" Then
                    leftTask = "Bubble" : rightTask = "Oddity"
                Else
                    leftTask = "Oddity" : rightTask = "Bubble"
                End If
            Case "E"
                ' sideCode = which side has 4 bubbles
                leftTask = "Bubble" : rightTask = "Bubble"
            Case "F"
                ' sideCode = which side has 4 oddity
                leftTask = "Oddity" : rightTask = "Oddity"
            Case "G", "H"
                If sideCode = "R" Then
                    leftTask = "None" : rightTask = "Bubble"
                Else
                    leftTask = "Bubble" : rightTask = "None"
                End If
            Case "I", "J"
                If sideCode = "R" Then
                    leftTask = "None" : rightTask = "Oddity"
                Else
                    leftTask = "Oddity" : rightTask = "None"
                End If
        End Select

        Select Case faceCode
            Case "1" : targetFace = "Happy" : isProbe = False : distractorType = "Neutral"
            Case "2" : targetFace = "Angry" : isProbe = False : distractorType = "Neutral"
            Case "3" : targetFace = "Fearful" : isProbe = False : distractorType = "Neutral"
            Case "4" : targetFace = "Happy" : isProbe = True : distractorType = "Inverted"
            Case "5" : targetFace = "Angry" : isProbe = True : distractorType = "Inverted"
            Case "6" : targetFace = "Fearful" : isProbe = True : distractorType = "Inverted"
            Case "0" : targetFace = "" : isProbe = False : distractorType = ""
        End Select

    End Sub


    ' ============================================
    ' GENERATE POSITIONS WITH OVERLAP CONSTRAINT
    ' ============================================
    Private Sub GeneratePositions()

        leftPositions.Clear()
        rightPositions.Clear()

        Dim allCells As New List(Of Integer)
        For i = 1 To 12 : allCells.Add(i) : Next
        ShuffleList(allCells)

        Select Case trialType

            Case "A", "B", "C", "D"
                Dim maxCount As Integer = Math.Max(bubbleCount, oddityCount)
                Dim minCount As Integer = Math.Min(bubbleCount, oddityCount)

                ' Big set = max stim count, small set = subset of big
                Dim bigSet As New List(Of Integer)(allCells.GetRange(0, maxCount))
                Dim bigShuffled As New List(Of Integer)(bigSet)
                ShuffleList(bigShuffled)
                Dim smallSet As New List(Of Integer)(bigShuffled.GetRange(0, minCount))

                Dim bubblePos, oddityPos As List(Of Integer)
                If bubbleCount >= oddityCount Then
                    bubblePos = bigSet : oddityPos = smallSet
                Else
                    oddityPos = bigSet : bubblePos = smallSet
                End If

                If leftTask = "Bubble" Then
                    leftPositions = bubblePos : rightPositions = oddityPos
                Else
                    leftPositions = oddityPos : rightPositions = bubblePos
                End If

                ' Target in overlap cell
                Dim overlapShuffled As New List(Of Integer)(smallSet)
                ShuffleList(overlapShuffled)
                Dim targetCell As Integer = overlapShuffled(0)
                If leftTask = "Oddity" Then
                    targetCellIndex = leftPositions.IndexOf(targetCell)
                Else
                    targetCellIndex = rightPositions.IndexOf(targetCell)
                End If

            Case "E"
                ' 4 bub vs 8 bub: 4 is subset of 8, sideCode = which has 4
                Dim big8 As New List(Of Integer)(allCells.GetRange(0, 8))
                Dim big8Shuffled As New List(Of Integer)(big8)
                ShuffleList(big8Shuffled)
                Dim small4 As New List(Of Integer)(big8Shuffled.GetRange(0, 4))

                If sideCode = "L" Then
                    leftPositions = small4 : rightPositions = big8
                Else
                    leftPositions = big8 : rightPositions = small4
                End If
                targetCellIndex = -1

            Case "F"
                ' 4 odd vs 8 odd: shared positions, 4 is subset of 8
                ' Target path: first 4 cells from overlap (exist on both sides),
                ' last 4 cells from 8-only positions
                Dim big8 As New List(Of Integer)(allCells.GetRange(0, 8))
                Dim big8Shuffled As New List(Of Integer)(big8)
                ShuffleList(big8Shuffled)
                Dim small4 As New List(Of Integer)(big8Shuffled.GetRange(0, 4))

                If sideCode = "L" Then
                    leftPositions = small4 : rightPositions = big8
                Else
                    leftPositions = big8 : rightPositions = small4
                End If

                ' Build predetermined target path:
                ' Steps 0-3: overlap cells (cells in small4), shuffled
                ' Steps 4-7: 8-only cells (in big8 but not small4), shuffled
                fTargetPath.Clear()
                fTargetPathStep.Clear()

                Dim overlapCells As New List(Of Integer)(small4)
                ShuffleList(overlapCells)

                Dim eightOnlyCells As New List(Of Integer)
                For Each cell In big8
                    If Not small4.Contains(cell) Then eightOnlyCells.Add(cell)
                Next
                ShuffleList(eightOnlyCells)

                For Each cell In overlapCells
                    fTargetPath.Add(cell)
                Next
                For Each cell In eightOnlyCells
                    fTargetPath.Add(cell)
                Next

                ' Target starts at first path cell (an overlap cell)
                Dim tCell As Integer = fTargetPath(0)
                targetCellIndex = leftPositions.IndexOf(tCell)
                fTypeRightTargetIndex = rightPositions.IndexOf(tCell)

                fTargetPathStep("L") = 0
                fTargetPathStep("R") = 0

                oddityCount = 4
                bubbleCount = 0

            Case "G", "H"
                Dim pos As New List(Of Integer)(allCells.GetRange(0, bubbleCount))
                If leftTask = "Bubble" Then leftPositions = pos Else rightPositions = pos
                targetCellIndex = -1

            Case "I", "J"
                Dim pos As New List(Of Integer)(allCells.GetRange(0, oddityCount))
                If leftTask = "Oddity" Then leftPositions = pos Else rightPositions = pos
                targetCellIndex = Rng.Next(0, oddityCount)

        End Select

    End Sub


    ' ============================================
    ' PLACE BUBBLES ON ONE SIDE
    ' ============================================
    Private Sub PlaceBubblesOnSide(rects() As Rectangle, positions As List(Of Integer),
                                   grid As System.Windows.Controls.Grid, alive() As Boolean)
        Dim count As Integer = positions.Count
        For i = 0 To count - 1
            rects(i).Fill = FindResource("BubbleBrush")
            PlaceInCell(rects(i), positions(i), grid)
            rects(i).Visibility = Visibility.Visible
            rects(i).IsEnabled = True
            rects(i).Tag = "Bubble"
            alive(i) = True
        Next
    End Sub


    ' ============================================
    ' PLACE ODDITY ON ONE SIDE
    ' ============================================
    Private Sub PlaceOddityOnSide(rects() As Rectangle, positions As List(Of Integer),
                                   grid As System.Windows.Controls.Grid, alive() As Boolean, isPrimary As Boolean)

        Dim count As Integer = positions.Count

        Dim targetBrushKey As String = ""
        Dim distractorBrushKey As String = ""

        Select Case targetFace
            Case "Happy" : targetBrushKey = "HappyBrush"
            Case "Angry" : targetBrushKey = "AngerBrush"
            Case "Fearful" : targetBrushKey = "FearBrush"
        End Select

        ' Standard trials: neutral distractors
        ' Probe trials: inverted-same-emotion distractors
        If isProbe Then
            Select Case targetFace
                Case "Happy" : distractorBrushKey = "HappyInvBrush"
                Case "Angry" : distractorBrushKey = "AngerInvBrush"
                Case "Fearful" : distractorBrushKey = "FearInvBrush"
            End Select
        Else
            distractorBrushKey = "NeutralBrush"
        End If

        Dim tIdx As Integer
        If isPrimary Then
            tIdx = targetCellIndex
        Else
            tIdx = Rng.Next(0, count)
        End If

        For i = 0 To count - 1
            If i = tIdx Then
                rects(i).Fill = FindResource(targetBrushKey)
                rects(i).Tag = "Target"
                If isPrimary Then oddityTargetRectIndex = i
            Else
                rects(i).Fill = FindResource(distractorBrushKey)
                rects(i).Tag = "Distractor"
            End If
            PlaceInCell(rects(i), positions(i), grid)
            rects(i).Visibility = Visibility.Visible
            rects(i).IsEnabled = True
            alive(i) = True
        Next

    End Sub


    ' ============================================
    ' PLACE RECT IN GRID CELL
    ' ============================================
    Private Sub PlaceInCell(rect As Rectangle, cell As Integer, grid As System.Windows.Controls.Grid)
        Dim row As Integer = (cell - 1) \ 3
        Dim col As Integer = (cell - 1) Mod 3
        System.Windows.Controls.Grid.SetRow(rect, row)
        System.Windows.Controls.Grid.SetColumn(rect, col)
        System.Windows.Controls.Grid.SetZIndex(rect, 10)
    End Sub


    ' ============================================
    ' UNIFIED TOUCH HANDLER
    ' ============================================
    ' Touch handler for MouseDown on stim rects (press/tap only).
    ' Signature uses MouseEventArgs (parent class of MouseButtonEventArgs)
    ' so it receives the MouseDown event. The handler doesn't use 'e'
    ' for anything — all needed info comes from sender (the Rectangle).
    Private Sub StimTouched(sender As Object, e As MouseEventArgs)

        If Not trialActive Then Exit Sub

        Dim rect As Rectangle = CType(sender, Rectangle)
        If Not rect.IsEnabled Then Exit Sub

        Dim side As String = ""
        Dim stimIndex As Integer = -1
        Dim stimTag As String = CStr(rect.Tag)

        For i = 0 To 7
            If rect Is leftRects(i) Then
                side = "L" : stimIndex = i : Exit For
            End If
            If rect Is rightRects(i) Then
                side = "R" : stimIndex = i : Exit For
            End If
        Next
        If stimIndex = -1 Then Exit Sub

        Dim cellRow As Integer = System.Windows.Controls.Grid.GetRow(rect)
        Dim cellCol As Integer = System.Windows.Controls.Grid.GetColumn(rect)
        Dim cellPos As Integer = (cellRow * 3) + cellCol + 1

        ' Latch first bubble cellPos for FirstBubbleGhost analysis
        If stimTag = "Bubble" AndAlso firstBubbleCellPos = -1 Then
            firstBubbleCellPos = cellPos
        End If

        ' Latch first-touch task for live metrics OOI computation
        If firstTouchTask = "" Then
            firstTouchTask = If(stimTag = "Bubble", "Bubble", "Oddity")
        End If

        ' Latch first-touch latency (any touch)
        If latencyFirstTouch < 0 Then
            latencyFirstTouch = trialStopwatch.ElapsedMilliseconds
        End If

        ' Latch first-target-touch latency (correct oddity target only)
        If latencyFirstTarget < 0 AndAlso stimTag = "Target" Then
            latencyFirstTarget = trialStopwatch.ElapsedMilliseconds
        End If

        Dim logEntry As String = String.Format("{0},{1},{2},{3},{4},{5},{6},{7}",
            trialStopwatch.ElapsedMilliseconds, side,
            If(side = "L", leftTask, rightTask),
            stimIndex, cellPos, stimTag, bubbleTouchCount, oddityWinCount)
        touchLog.Add(logEntry)

        Select Case stimTag
            Case "Bubble"
                HandleBubbleTouch(rect, stimIndex, side)
            Case "Target"
                HandleOddityTargetTouch(rect, stimIndex, side)
            Case "Distractor"
                HandleOddityDistractorTouch(rect, stimIndex, side)
        End Select

    End Sub


    ' ============================================
    ' LAYOUT LOGGING HELPERS
    ' Used by RecordTrialData to add ghost-touch analysis columns.
    ' ============================================
    Private Function FormatPositionList(positions As List(Of Integer)) As String
        If positions Is Nothing OrElse positions.Count = 0 Then Return ""
        Dim parts As New List(Of String)
        For Each p In positions
            parts.Add(p.ToString())
        Next
        Return String.Join("|", parts)
    End Function

    Private Function ComputeTargetCellPos() As Integer
        ' Returns the cellPos (1-12) of the primary oddity target, or -1 if
        ' the trial has no oddity target. For F-trials (both sides oddity),
        ' returns the left-side initial target cellPos (which equals the
        ' right-side initial target cellPos by design — both start at the
        ' same overlap cell).
        Select Case trialType
            Case "A", "B", "C", "D"
                If leftTask = "Oddity" Then
                    If targetCellIndex >= 0 AndAlso targetCellIndex < leftPositions.Count Then
                        Return leftPositions(targetCellIndex)
                    End If
                Else
                    If targetCellIndex >= 0 AndAlso targetCellIndex < rightPositions.Count Then
                        Return rightPositions(targetCellIndex)
                    End If
                End If
            Case "F"
                If targetCellIndex >= 0 AndAlso targetCellIndex < leftPositions.Count Then
                    Return leftPositions(targetCellIndex)
                End If
            Case "I", "J"
                If leftTask = "Oddity" Then
                    If targetCellIndex >= 0 AndAlso targetCellIndex < leftPositions.Count Then
                        Return leftPositions(targetCellIndex)
                    End If
                Else
                    If targetCellIndex >= 0 AndAlso targetCellIndex < rightPositions.Count Then
                        Return rightPositions(targetCellIndex)
                    End If
                End If
        End Select
        Return -1
    End Function

    Private Function ComputeTargetSide() As String
        Select Case trialType
            Case "A", "B", "C", "D", "I", "J"
                Return If(leftTask = "Oddity", "L", "R")
            Case "F"
                Return "B"  ' Both sides
            Case Else
                Return "-"
        End Select
    End Function


    ' ============================================
    ' LIVE METRICS — aggregation, formatting, and save
    ' ============================================

    Private Sub ResetMetricsAggregators()
        trialTimes.Clear()
        For i As Integer = 0 To 3
            mt_trialsByType(i) = 0
            mt_bubCompleteByType(i) = 0
            mt_firstTouchBubByType(i) = 0
            mt_ghostFirstByType(i) = 0
            mt_bubAttemptByType(i) = 0
            mt_switchesByType(i) = 0
            mt_zeroSwitchByType(i) = 0
            mt_oneSwitchByType(i) = 0
            mt_twoPlusSwitchByType(i) = 0
            mt_ooiSumByType(i) = 0.0
            mt_oddCompleteTouchesByType(i) = 0
            mt_oddCompleteTrialsByType(i) = 0
        Next
        mt_F_4side_TouchesSum = 0
        mt_F_4side_Count = 0
        mt_F_8side_TouchesSum = 0
        mt_F_8side_Count = 0
        mt_sessionBubbleTouches = 0
        mt_sessionOddityTouches = 0
        For i As Integer = 0 To 2
            mt_trialsByEmotionAD(i) = 0
            mt_bubCompleteByEmotionAD(i) = 0
            mt_firstTouchBubByEmotionAD(i) = 0
            mt_ghostFirstByEmotionAD(i) = 0
            mt_bubAttemptByEmotionAD(i) = 0
            mt_chose_preTwoErr(i) = 0
            mt_chose_preTwoCorrect(i) = 0
            mt_forced_preTwoErr(i) = 0
            mt_forced_preTwoCorrect(i) = 0
            mt_chose_twoStimWin(i) = 0
            mt_chose_twoStimLoss(i) = 0
            mt_forced_twoStimWin(i) = 0
            mt_forced_twoStimLoss(i) = 0
            mt_targetLatencySum(i) = 0
            mt_targetLatencyCount(i) = 0
        Next
    End Sub

    ' Map "A"/"B"/"C"/"D" to 0/1/2/3, or -1 if not A-D
    Private Function TypeIndex(t As String) As Integer
        Select Case t
            Case "A" : Return 0
            Case "B" : Return 1
            Case "C" : Return 2
            Case "D" : Return 3
            Case Else : Return -1
        End Select
    End Function

    ' Map targetFace string to 0/1/2 (Angry/Happy/Fearful), or -1 if no emotion
    Private Function EmotionIndex(face As String) As Integer
        Select Case face
            Case "Angry" : Return 0
            Case "Happy" : Return 1
            Case "Fearful" : Return 2
            Case Else : Return -1
        End Select
    End Function

    ' Count task switches by walking touchLog (entries semicolon-separated).
    ' A switch is a transition between Bubble-tagged and Target/Distractor-tagged
    ' touches in consecutive entries. Empty stimTag entries don't exist in this
    ' build (no empty-cell logging).
    Private Function CountTaskSwitches() As Integer
        If touchLog.Count < 2 Then Return 0
        Dim switches As Integer = 0
        Dim prevSide As String = ""  ' "B" = bubble, "O" = oddity
        For Each entry In touchLog
            Dim parts() As String = entry.Split(","c)
            If parts.Length < 6 Then Continue For
            Dim tag As String = parts(5)
            Dim curSide As String
            If tag = "Bubble" Then
                curSide = "B"
            Else
                curSide = "O"
            End If
            If prevSide <> "" AndAlso curSide <> prevSide Then
                switches += 1
            End If
            prevSide = curSide
        Next
        Return switches
    End Function

    ' Walk touchLog and count pre-2-stim oddity correct and error touches,
    ' returned as (correct, errors). At each oddity touch, the touchLog
    ' entry's bubbleTouchCount and oddityWinCount tell us the state. We
    ' count an oddity Target touch as pre-2-stim correct if the count of
    ' alive oddity stim BEFORE the touch was >= 3 (i.e. perceptual stage).
    ' For Distractor touches, same threshold defines pre-2-stim errors.
    ' OddTwoStimWin handles the 2-stim level separately so we exclude that.
    ' For F trials (oddity vs oddity), determine which side the subject
    ' completed and how many total touches it took on that side.
    ' Returns sideStim = 4 or 8 (which size completed), and totalTouches
    ' = target + distractor touches on that side. Returns -1 / -1 if
    ' not a completed F trial.
    Private Sub ComputeFCompletingSide(ByRef sideStim As Integer, ByRef totalTouches As Integer)
        sideStim = -1
        totalTouches = -1
        If trialType <> "F" OrElse completedBy <> "Oddity" Then Exit Sub

        Dim lTargets As Integer = 0, lDist As Integer = 0
        Dim rTargets As Integer = 0, rDist As Integer = 0
        For Each entry In touchLog
            Dim parts() As String = entry.Split(","c)
            If parts.Length < 6 Then Continue For
            If parts(2) <> "Oddity" Then Continue For
            If parts(5) = "Target" Then
                If parts(1) = "L" Then lTargets += 1 Else rTargets += 1
            ElseIf parts(5) = "Distractor" Then
                If parts(1) = "L" Then lDist += 1 Else rDist += 1
            End If
        Next

        ' The completing side has target count equal to its stim count
        If lTargets = leftPositions.Count Then
            sideStim = leftPositions.Count
            totalTouches = lTargets + lDist
        ElseIf rTargets = rightPositions.Count Then
            sideStim = rightPositions.Count
            totalTouches = rTargets + rDist
        End If
    End Sub

    Private Sub CountOddityPreTwoTouches(ByRef correct As Integer, ByRef errs As Integer)
        correct = 0
        errs = 0
        ' Reconstruct oddity-alive count from oddityTotal and oddityWinCount.
        ' At each touchLog entry, the pre-touch alive count = oddityTotal - oddityWinCount.
        ' (Distractor touches don't decrement aliveCount; correct touches do.)
        For Each entry In touchLog
            Dim parts() As String = entry.Split(","c)
            If parts.Length < 8 Then Continue For
            Dim tag As String = parts(5)
            If tag <> "Target" AndAlso tag <> "Distractor" Then Continue For
            Dim winCountAtTouch As Integer
            If Not Integer.TryParse(parts(7), winCountAtTouch) Then Continue For
            Dim alivePreTouch As Integer = oddityTotal - winCountAtTouch
            If alivePreTouch >= 3 Then
                If tag = "Target" Then
                    correct += 1
                Else
                    errs += 1
                End If
            End If
        Next
    End Sub

    ' Called once per completed trial from RecordTrialData.
    Private Sub UpdateMetricsForTrial()
        Dim tIdx As Integer = TypeIndex(trialType)
        Dim eIdx As Integer = EmotionIndex(targetFace)

        trialTimes.Add(trialStopwatch.ElapsedMilliseconds)

        ' New trial data → both streams now have unsaved changes
        dataStreamSaved = False
        metricsSaved = False

        ' Session-cumulative touch counts (all trial types)
        mt_sessionBubbleTouches += bubbleTouchCount
        mt_sessionOddityTouches += (oddityWinCount + oddityErrorCount)

        ' Latency to first target by emotion (any trial with a target touched)
        If eIdx >= 0 AndAlso latencyFirstTarget >= 0 Then
            mt_targetLatencySum(eIdx) += latencyFirstTarget
            mt_targetLatencyCount(eIdx) += 1
        End If

        ' Pre-2-stim oddity touches by emotion (for chose vs forced)
        Dim preCorrect As Integer = 0
        Dim preErrs As Integer = 0
        CountOddityPreTwoTouches(preCorrect, preErrs)

        ' Oddity context: chose-into-oddity (A-D, completed by oddity) or forced (I,J)
        If eIdx >= 0 Then
            If tIdx >= 0 AndAlso completedBy = "Oddity" Then
                mt_chose_preTwoCorrect(eIdx) += preCorrect
                mt_chose_preTwoErr(eIdx) += preErrs
                If oddTwoStimWin = "1" Then mt_chose_twoStimWin(eIdx) += 1
                If oddTwoStimWin = "0" Then mt_chose_twoStimLoss(eIdx) += 1
            ElseIf trialType = "I" OrElse trialType = "J" Then
                mt_forced_preTwoCorrect(eIdx) += preCorrect
                mt_forced_preTwoErr(eIdx) += preErrs
                If oddTwoStimWin = "1" Then mt_forced_twoStimWin(eIdx) += 1
                If oddTwoStimWin = "0" Then mt_forced_twoStimLoss(eIdx) += 1
            End If
        End If

        ' F-trial performance (oddity vs oddity)
        If trialType = "F" AndAlso completedBy = "Oddity" Then
            Dim fSideStim As Integer = -1, fSideTouches As Integer = -1
            ComputeFCompletingSide(fSideStim, fSideTouches)
            If fSideStim = 4 Then
                mt_F_4side_TouchesSum += fSideTouches
                mt_F_4side_Count += 1
            ElseIf fSideStim = 8 Then
                mt_F_8side_TouchesSum += fSideTouches
                mt_F_8side_Count += 1
            End If
        End If

        ' Type-and-emotion aggregations are A-D only
        If tIdx < 0 Then
            UpdateMetricsDisplay()
            Exit Sub
        End If

        mt_trialsByType(tIdx) += 1
        If eIdx >= 0 Then mt_trialsByEmotionAD(eIdx) += 1

        If completedBy = "Bubble" Then
            mt_bubCompleteByType(tIdx) += 1
            If eIdx >= 0 Then mt_bubCompleteByEmotionAD(eIdx) += 1
        ElseIf completedBy = "Oddity" Then
            mt_oddCompleteTouchesByType(tIdx) += (oddityWinCount + oddityErrorCount)
            mt_oddCompleteTrialsByType(tIdx) += 1
        End If

        If firstTouchTask = "Bubble" Then
            mt_firstTouchBubByType(tIdx) += 1
            If eIdx >= 0 Then mt_firstTouchBubByEmotionAD(eIdx) += 1
        End If

        ' Ghost-first metrics: only for trials where some bubble was touched
        If firstBubbleCellPos > 0 Then
            mt_bubAttemptByType(tIdx) += 1
            If eIdx >= 0 Then mt_bubAttemptByEmotionAD(eIdx) += 1
            If firstBubbleCellPos = ComputeTargetCellPos() Then
                mt_ghostFirstByType(tIdx) += 1
                If eIdx >= 0 Then mt_ghostFirstByEmotionAD(eIdx) += 1
            End If
        End If

        ' Switches per trial
        Dim swCount As Integer = CountTaskSwitches()
        mt_switchesByType(tIdx) += swCount
        If swCount = 0 Then
            mt_zeroSwitchByType(tIdx) += 1
        ElseIf swCount = 1 Then
            mt_oneSwitchByType(tIdx) += 1
        Else
            mt_twoPlusSwitchByType(tIdx) += 1
        End If

        ' Per-trial OOI (dual-task A-D only)
        Dim totalTouches As Integer = bubbleTouchCount + oddityWinCount + oddityErrorCount
        Dim bubFrac As Double = 0
        If totalTouches > 0 Then bubFrac = bubbleTouchCount / CDbl(totalTouches)
        Dim firstBub As Double = If(firstTouchTask = "Bubble", 1.0, 0.0)
        Dim bubCompl As Double = If(completedBy = "Bubble", 1.0, 0.0)
        Dim ooi As Double = 0.5 * bubFrac + 0.3 * firstBub + 0.2 * bubCompl
        mt_ooiSumByType(tIdx) += ooi

        UpdateMetricsDisplay()
    End Sub

    Private Function Pct(num As Integer, denom As Integer) As String
        If denom = 0 Then Return "—"
        Return Math.Round(100.0 * num / denom).ToString() & "%"
    End Function

    Private Function MeanOOI(tIdx As Integer) As String
        If mt_trialsByType(tIdx) = 0 Then Return "—"
        Return (mt_ooiSumByType(tIdx) / mt_trialsByType(tIdx)).ToString("0.00")
    End Function

    ' Mean oddity touches to complete (when subject chose oddity in A-D).
    ' Compare to type's OddN (4 for A,B; 8 for C,D) — extra touches = errors.
    Private Function MeanOddTouches(tIdx As Integer) As String
        If mt_oddCompleteTrialsByType(tIdx) = 0 Then Return "—"
        Return (mt_oddCompleteTouchesByType(tIdx) / CDbl(mt_oddCompleteTrialsByType(tIdx))).ToString("0.0")
    End Function

    ' Mean touches on F-trial completing side (4-stim or 8-stim).
    Private Function MeanFSide(touchSum As Integer, count As Integer) As String
        If count = 0 Then Return "—"
        Return (touchSum / CDbl(count)).ToString("0.0")
    End Function

    Private Function OverallOOI() As String
        Dim totalTrials As Integer = 0
        Dim totalSum As Double = 0
        For i As Integer = 0 To 3
            totalTrials += mt_trialsByType(i)
            totalSum += mt_ooiSumByType(i)
        Next
        If totalTrials = 0 Then Return "—"
        Return (totalSum / totalTrials).ToString("0.00")
    End Function

    Private Function FormatDuration(ms As Long) As String
        Dim totalSec As Long = ms \ 1000
        Dim mins As Long = totalSec \ 60
        Dim secs As Long = totalSec Mod 60
        Return String.Format("{0}m {1:D2}s", mins, secs)
    End Function

    ' Estimate remaining session time = mean trial time * trials left.
    ' Returns "—" before any trials complete (no basis for estimate).
    Private Function EstRemaining(trialsCompleted As Integer) As String
        If trialTimes.Count = 0 Then Return "—"
        If trialsCompleted >= 60 Then Return "0m 00s"
        Dim sum As Long = 0
        For Each x In trialTimes
            sum += x
        Next
        Dim meanMs As Long = sum \ trialTimes.Count
        Dim remaining As Long = meanMs * (60 - trialsCompleted)
        Return "~" & FormatDuration(remaining)
    End Function

    Private Function MeanTrialTime(ms As IEnumerable(Of Long)) As String
        Dim count As Integer = 0
        Dim sum As Long = 0
        For Each x In ms
            sum += x
            count += 1
        Next
        If count = 0 Then Return "—"
        Dim meanMs As Long = sum \ count
        Return (meanMs / 1000.0).ToString("0.0") & "s"
    End Function

    Private Sub UpdateMetricsDisplay()
        Dim sb As New System.Text.StringBuilder()
        Dim totalTrials As Integer = mt_trialsByType(0) + mt_trialsByType(1) + mt_trialsByType(2) + mt_trialsByType(3)
        Dim trialsCompleted As Integer = trialTimes.Count
        Dim elapsedMs As Long = CLng((DateTime.Now - sessionStartTime).TotalMilliseconds)

        sb.AppendLine("=== SESSION PROGRESS ===")
        sb.AppendLine(String.Format("Trial: {0} / 60     Elapsed: {1}     Est. remaining: {2}",
            trialsCompleted, FormatDuration(elapsedMs), EstRemaining(trialsCompleted)))
        sb.AppendLine(String.Format("Mean trial: {0}     Last 5: {1}",
            MeanTrialTime(trialTimes),
            MeanTrialTime(trialTimes.Skip(Math.Max(0, trialTimes.Count - 5)))))
        sb.AppendLine(String.Format("Bubble touches: {0}     Oddity touches: {1}",
            mt_sessionBubbleTouches, mt_sessionOddityTouches))
        sb.AppendLine()

        sb.AppendLine("=== OPT-OUT & PERFORMANCE (A-D) ===  BubCompl  FirstBub  GhostRate     OddTouches")
        Dim typeNames() As String = {"A (4/4)", "B (8/4)", "C (4/8)", "D (8/8)"}
        Dim oddOptimums() As Integer = {4, 4, 8, 8}
        For i As Integer = 0 To 3
            sb.AppendLine(String.Format("{0,-10}                          {1,5}    {2,5}    {3,5} ({4}/{5})    {6} / {7}",
                typeNames(i),
                Pct(mt_bubCompleteByType(i), mt_trialsByType(i)),
                Pct(mt_firstTouchBubByType(i), mt_trialsByType(i)),
                Pct(mt_ghostFirstByType(i), mt_bubAttemptByType(i)),
                mt_ghostFirstByType(i), mt_bubAttemptByType(i),
                MeanOddTouches(i), oddOptimums(i)))
        Next
        sb.AppendLine(String.Format("F (4 vs 8 odd, forced)        4-side: {0} / 4 (n={1})   8-side: {2} / 8 (n={3})",
            MeanFSide(mt_F_4side_TouchesSum, mt_F_4side_Count), mt_F_4side_Count,
            MeanFSide(mt_F_8side_TouchesSum, mt_F_8side_Count), mt_F_8side_Count))
        sb.AppendLine()

        sb.AppendLine("By emotion (combined A-D):")
        Dim emoNames() As String = {"Angry  ", "Happy  ", "Fearful"}
        For i As Integer = 0 To 2
            sb.AppendLine(String.Format("{0}         {1,5}    {2,5}    {3,5}",
                emoNames(i),
                Pct(mt_bubCompleteByEmotionAD(i), mt_trialsByEmotionAD(i)),
                Pct(mt_firstTouchBubByEmotionAD(i), mt_trialsByEmotionAD(i)),
                Pct(mt_ghostFirstByEmotionAD(i), mt_bubAttemptByEmotionAD(i))))
        Next
        sb.AppendLine()

        sb.AppendLine("=== ODDITY PERFORMANCE ===  Chose    Forced")
        For i As Integer = 0 To 2
            Dim choseDenom As Integer = mt_chose_preTwoErr(i) + mt_chose_preTwoCorrect(i)
            Dim forcedDenom As Integer = mt_forced_preTwoErr(i) + mt_forced_preTwoCorrect(i)
            sb.AppendLine(String.Format("{0} pre-2 err   {1,5}    {2,5}",
                emoNames(i),
                Pct(mt_chose_preTwoErr(i), choseDenom),
                Pct(mt_forced_preTwoErr(i), forcedDenom)))
        Next
        Dim choseTwoSum As Integer, forcedTwoSum As Integer
        Dim choseTwoErr As Integer, forcedTwoErr As Integer
        For i As Integer = 0 To 2
            choseTwoSum += mt_chose_twoStimWin(i) + mt_chose_twoStimLoss(i)
            forcedTwoSum += mt_forced_twoStimWin(i) + mt_forced_twoStimLoss(i)
            choseTwoErr += mt_chose_twoStimLoss(i)
            forcedTwoErr += mt_forced_twoStimLoss(i)
        Next
        sb.AppendLine(String.Format("2-stim err overall   {0,5}    {1,5}",
            Pct(choseTwoErr, choseTwoSum), Pct(forcedTwoErr, forcedTwoSum)))
        sb.AppendLine()

        sb.AppendLine("=== WAVERING (A-D) ===")
        Dim zSum As Integer, oSum As Integer, tSum As Integer, swSum As Integer, trialsSum As Integer
        For i As Integer = 0 To 3
            zSum += mt_zeroSwitchByType(i)
            oSum += mt_oneSwitchByType(i)
            tSum += mt_twoPlusSwitchByType(i)
            swSum += mt_switchesByType(i)
            trialsSum += mt_trialsByType(i)
        Next
        sb.AppendLine(String.Format("0 sw: {0}   1: {1}   2+: {2}",
            Pct(zSum, trialsSum), Pct(oSum, trialsSum), Pct(tSum, trialsSum)))
        sb.AppendLine(String.Format("Mean switches/trial: {0}",
            If(trialsSum = 0, "—", (swSum / CDbl(trialsSum)).ToString("0.0"))))
        sb.AppendLine()

        sb.AppendLine("=== LATENCY TO TARGET (by emotion) ===")
        For i As Integer = 0 To 2
            Dim mean As String
            If mt_targetLatencyCount(i) = 0 Then
                mean = "—"
            Else
                Dim s As Double = mt_targetLatencySum(i) / CDbl(mt_targetLatencyCount(i)) / 1000.0
                mean = s.ToString("0.00") & "s"
            End If
            sb.AppendLine(String.Format("{0}    {1,8}  (n={2})",
                emoNames(i), mean, mt_targetLatencyCount(i)))
        Next
        sb.AppendLine()

        sb.AppendLine("=== CUMULATIVE OOI ===")
        sb.AppendLine(String.Format("Overall: {0}    A: {1}    B: {2}    C: {3}    D: {4}",
            OverallOOI(), MeanOOI(0), MeanOOI(1), MeanOOI(2), MeanOOI(3)))

        tbMetrics.Text = sb.ToString()
    End Sub

    Private Sub SaveMetrics_Click(sender As Object, e As System.Windows.RoutedEventArgs)
        Try
            Dim dialog As New Microsoft.Win32.SaveFileDialog()
            Dim defaultName As String = String.Format("{0}_Session{1}_{2:yyyyMMdd_HHmmss}_metrics.txt",
                If(String.IsNullOrEmpty(subjectName), "Subject", subjectName),
                sessionNumber,
                DateTime.Now)
            dialog.FileName = defaultName
            dialog.DefaultExt = ".txt"
            dialog.Filter = "Text files (*.txt)|*.txt|All files (*.*)|*.*"
            If dialog.ShowDialog() = True Then
                Dim sb As New System.Text.StringBuilder()
                sb.AppendLine("SafetyPop Session Metrics")
                sb.AppendLine("=========================")
                sb.AppendLine("Subject:   " & subjectName)
                sb.AppendLine("Species:   " & speciesName)
                sb.AppendLine("Date:      " & datestring)
                sb.AppendLine("Session:   " & sessionNumber)
                sb.AppendLine("Location:  " & locationName)
                sb.AppendLine("Saved:     " & DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"))
                sb.AppendLine()
                sb.AppendLine(tbMetrics.Text)
                System.IO.File.WriteAllText(dialog.FileName, sb.ToString())
                metricsSaved = True
            End If
        Catch ex As Exception
            System.Windows.MessageBox.Show("Save failed: " & ex.Message)
        End Try
    End Sub
    ' touch one -> all disappear -> pause -> survivors reappear
    ' ============================================
    Private Async Sub HandleBubbleTouch(rect As Rectangle, index As Integer, side As String)

        bubbleSound.Play()
        trialActive = False

        Dim bubRects() As Rectangle
        Dim bubAlive() As Boolean
        If side = "L" Then
            bubRects = leftRects : bubAlive = leftAlive
        Else
            bubRects = rightRects : bubAlive = rightAlive
        End If

        ' Kill the touched bubble permanently
        KillStim(rect)
        bubAlive(index) = False
        bubbleTouchCount += 1
        lblBubbleTouches.Content = bubbleTouchCount

        ' Kill all remaining bubbles visually (they stay alive for revive)
        For i = 0 To 7
            If bubAlive(i) AndAlso CStr(bubRects(i).Tag) = "Bubble" Then
                KillStim(bubRects(i))
            End If
        Next

        ' Count survivors
        Dim remaining As Integer = 0
        For i = 0 To 7
            If bubAlive(i) AndAlso CStr(bubRects(i).Tag) = "Bubble" Then remaining += 1
        Next

        If remaining = 0 Then
            ' All bubbles popped — trial complete
            trialActive = True
            FinishTrial("Bubble")
            Exit Sub
        End If

        ' Pause same as oddity
        Await Task.Delay(500)

        ' Revive surviving bubbles (clear kill animation first)
        For i = 0 To 7
            If bubAlive(i) AndAlso CStr(bubRects(i).Tag) = "Bubble" Then
                bubRects(i).BeginAnimation(Rectangle.WidthProperty, Nothing)
                bubRects(i).BeginAnimation(Rectangle.HeightProperty, Nothing)
                bubRects(i).BeginAnimation(Rectangle.OpacityProperty, Nothing)
                bubRects(i).Opacity = 1
                bubRects(i).Visibility = Visibility.Visible
                ReviveStim(bubRects(i))
                bubRects(i).IsEnabled = True
            End If
        Next

        trialActive = True

    End Sub


    ' ============================================
    ' ODDITY TARGET TOUCH
    ' ============================================
    Private Sub HandleOddityTargetTouch(rect As Rectangle, index As Integer, side As String)

        clickSound.Play()
        oddityWinCount += 1
        lblOddityWins.Content = oddityWinCount

        Dim oddRects() As Rectangle
        Dim oddAlive() As Boolean
        If side = "L" Then
            oddRects = leftRects : oddAlive = leftAlive
        Else
            oddRects = rightRects : oddAlive = rightAlive
        End If

        ' Count remaining oddity stim (including the one just touched)
        oddityRemaining = 0
        For i = 0 To 7
            If oddAlive(i) AndAlso (CStr(oddRects(i).Tag) = "Target" OrElse CStr(oddRects(i).Tag) = "Distractor") Then
                oddityRemaining += 1
            End If
        Next

        ' 2-stim choice detection: if there were exactly 2 stim alive at the
        ' moment of this target touch (i.e., target + 1 distractor), the
        ' subject just made a correct 2-stim choice. Record once per trial.
        If oddityRemaining = 2 AndAlso oddTwoStimWin = "NA" Then
            oddTwoStimWin = "1"
        End If

        If oddityRemaining = 1 Then
            ' Solo target was touched — side complete
            If trialType = "F" Then
                FinishTrial("Oddity")  ' Either side completing ends the trial
            Else
                FinishTrial("Oddity")
            End If
        ElseIf oddityRemaining = 2 Then
            OdditySoloReset(rect, index, side)
        Else
            OddityProgressiveReset(rect, index, side)
        End If

    End Sub


    ' ============================================
    ' ODDITY DISTRACTOR TOUCH
    ' Cost: all stim on this side disappear and reappear
    ' with same timing as correct touches. No progress.
    ' ============================================
    Private Async Sub HandleOddityDistractorTouch(rect As Rectangle, index As Integer, side As String)
        oddityErrorCount += 1
        lblOddityErrors.Content = oddityErrorCount
        popSound.Play()

        Dim oddRects() As Rectangle
        Dim oddAlive() As Boolean
        If side = "L" Then
            oddRects = leftRects : oddAlive = leftAlive
        Else
            oddRects = rightRects : oddAlive = rightAlive
        End If

        ' 2-stim choice detection: if exactly 2 oddity stim were alive on this
        ' side at the moment of the distractor touch, the subject just made an
        ' incorrect 2-stim choice. Record once per trial.
        If oddTwoStimWin = "NA" Then
            Dim aliveOddityCount As Integer = 0
            For i = 0 To 7
                If oddAlive(i) AndAlso (CStr(oddRects(i).Tag) = "Target" OrElse CStr(oddRects(i).Tag) = "Distractor") Then
                    aliveOddityCount += 1
                End If
            Next
            If aliveOddityCount = 2 Then
                oddTwoStimWin = "0"
            End If
        End If

        ' Kill all oddity stim on this side
        For i = 0 To 7
            If oddAlive(i) AndAlso (CStr(oddRects(i).Tag) = "Target" OrElse CStr(oddRects(i).Tag) = "Distractor") Then
                KillStim(oddRects(i))
            End If
        Next

        ' Same pause as correct touches
        Await Task.Delay(500)

        ' Revive all in same positions
        For i = 0 To 7
            If oddAlive(i) AndAlso (CStr(oddRects(i).Tag) = "Target" OrElse CStr(oddRects(i).Tag) = "Distractor") Then
                oddRects(i).BeginAnimation(Rectangle.WidthProperty, Nothing)
                oddRects(i).BeginAnimation(Rectangle.HeightProperty, Nothing)
                oddRects(i).BeginAnimation(Rectangle.OpacityProperty, Nothing)
                oddRects(i).Opacity = 1
                oddRects(i).Visibility = Visibility.Visible
                ReviveStim(oddRects(i))
                oddRects(i).IsEnabled = True
            End If
        Next
    End Sub


    ' ============================================
    ' ODDITY SOLO RESET (2 remaining -> solo target)
    ' ============================================
    Private Async Sub OdditySoloReset(touchedTarget As Rectangle, targetIdx As Integer, side As String)

        trialActive = False

        Dim oddRects() As Rectangle
        Dim oddAlive() As Boolean
        Dim oddGrid As System.Windows.Controls.Grid
        Dim oddPositions As List(Of Integer)
        If side = "L" Then
            oddRects = leftRects : oddAlive = leftAlive : oddGrid = LeftGrid : oddPositions = leftPositions
        Else
            oddRects = rightRects : oddAlive = rightAlive : oddGrid = RightGrid : oddPositions = rightPositions
        End If

        ' Kill the touched target
        KillStim(touchedTarget)
        oddAlive(targetIdx) = False

        ' Find the last distractor's position before killing it
        Dim lastDistractorRow As Integer = 0
        Dim lastDistractorCol As Integer = 0
        For i = 0 To 7
            If oddAlive(i) AndAlso CStr(oddRects(i).Tag) = "Distractor" Then
                lastDistractorRow = System.Windows.Controls.Grid.GetRow(oddRects(i))
                lastDistractorCol = System.Windows.Controls.Grid.GetColumn(oddRects(i))
                KillStim(oddRects(i))
                oddAlive(i) = False
            End If
        Next

        Await Task.Delay(500)

        ' Determine solo target placement
        Dim soloRow As Integer
        Dim soloCol As Integer

        If trialType = "F" Then
            ' F-trial: use next cell from predetermined path
            fTargetPathStep(side) += 1
            Dim nextCell As Integer = fTargetPath(fTargetPathStep(side))
            soloRow = (nextCell - 1) \ 3
            soloCol = (nextCell - 1) Mod 3
        Else
            ' Standard: place where the distractor was
            soloRow = lastDistractorRow
            soloCol = lastDistractorCol
        End If

        ' Reuse the target rect
        Dim soloIdx As Integer = targetIdx
        Dim targetBrushKey As String = GetTargetBrushKey()
        oddRects(soloIdx).Fill = FindResource(targetBrushKey)
        oddRects(soloIdx).Tag = "Target"
        System.Windows.Controls.Grid.SetRow(oddRects(soloIdx), soloRow)
        System.Windows.Controls.Grid.SetColumn(oddRects(soloIdx), soloCol)
        System.Windows.Controls.Grid.SetZIndex(oddRects(soloIdx), 10)
        oddAlive(soloIdx) = True
        oddityTargetRectIndex = soloIdx
        oddityRemaining = 1

        ReviveStim(oddRects(soloIdx))
        oddRects(soloIdx).IsEnabled = True

        trialActive = True

    End Sub


    ' ============================================
    ' ODDITY PROGRESSIVE ELIMINATION
    ' ============================================
    Private Async Sub OddityProgressiveReset(touchedTarget As Rectangle, targetIdx As Integer, side As String)

        trialActive = False

        Dim oddRects() As Rectangle
        Dim oddAlive() As Boolean
        Dim oddGrid As System.Windows.Controls.Grid
        Dim oddPositions As List(Of Integer)
        If side = "L" Then
            oddRects = leftRects : oddAlive = leftAlive : oddGrid = LeftGrid : oddPositions = leftPositions
        Else
            oddRects = rightRects : oddAlive = rightAlive : oddGrid = RightGrid : oddPositions = rightPositions
        End If

        ' Kill the touched target
        KillStim(touchedTarget)
        oddAlive(targetIdx) = False

        ' Kill all distractors visually (they stay alive for revive)
        For i = 0 To 7
            If oddAlive(i) AndAlso CStr(oddRects(i).Tag) = "Distractor" Then
                KillStim(oddRects(i))
            End If
        Next

        Await Task.Delay(500)

        ' Collect surviving distractors (oddAlive still true, just visually killed)
        Dim survivors As New List(Of Integer)
        For i = 0 To 7
            If oddAlive(i) AndAlso CStr(oddRects(i).Tag) = "Distractor" Then
                survivors.Add(i)
            End If
        Next

        ' Pick new target from survivors
        If survivors.Count > 0 Then
            Dim newTargetIdx As Integer
            Dim targetBrushKey As String = GetTargetBrushKey()

            If trialType = "F" Then
                ' F-trial: advance path step, pick the survivor that is in the path cell
                ' If no survivor is at that cell, pick any survivor and move it there
                fTargetPathStep(side) += 1
                Dim nextCell As Integer = fTargetPath(fTargetPathStep(side))
                Dim nextRow As Integer = (nextCell - 1) \ 3
                Dim nextCol As Integer = (nextCell - 1) Mod 3

                ' Try to find a survivor already at the path cell
                newTargetIdx = -1
                For Each si In survivors
                    Dim sr As Integer = System.Windows.Controls.Grid.GetRow(oddRects(si))
                    Dim sc As Integer = System.Windows.Controls.Grid.GetColumn(oddRects(si))
                    If sr = nextRow AndAlso sc = nextCol Then
                        newTargetIdx = si
                        Exit For
                    End If
                Next

                ' If none found at that cell, pick first survivor and reposition
                If newTargetIdx = -1 Then
                    newTargetIdx = survivors(0)
                    System.Windows.Controls.Grid.SetRow(oddRects(newTargetIdx), nextRow)
                    System.Windows.Controls.Grid.SetColumn(oddRects(newTargetIdx), nextCol)
                End If
            Else
                ' Standard: random survivor becomes target
                ShuffleList(survivors)
                newTargetIdx = survivors(0)
            End If

            oddRects(newTargetIdx).Fill = FindResource(targetBrushKey)
            oddRects(newTargetIdx).Tag = "Target"
            oddityTargetRectIndex = newTargetIdx
        End If

        ' Revive all surviving oddity stim (clear old animations first)
        For i = 0 To 7
            If oddAlive(i) AndAlso CStr(oddRects(i).Tag) <> "Bubble" Then
                ' Must clear the kill animation before reviving
                oddRects(i).BeginAnimation(Rectangle.WidthProperty, Nothing)
                oddRects(i).BeginAnimation(Rectangle.HeightProperty, Nothing)
                oddRects(i).BeginAnimation(Rectangle.OpacityProperty, Nothing)
                oddRects(i).Opacity = 1
                oddRects(i).Visibility = Visibility.Visible
                ReviveStim(oddRects(i))
                oddRects(i).IsEnabled = True
            End If
        Next

        ' Update count
        oddityRemaining = 0
        For i = 0 To 7
            If oddAlive(i) AndAlso CStr(oddRects(i).Tag) <> "Bubble" Then
                oddityRemaining += 1
            End If
        Next

        trialActive = True

    End Sub

    Private Function GetTargetBrushKey() As String
        Select Case targetFace
            Case "Happy" : Return "HappyBrush"
            Case "Angry" : Return "AngerBrush"
            Case "Fearful" : Return "FearBrush"
            Case Else : Return "HappyBrush"
        End Select
    End Function


    ' ============================================
    ' TRIAL COMPLETION
    ' ============================================
    Private Async Sub FinishTrial(completedBy As String)

        trialActive = False
        My.Settings.Pelletgo = True
        trialStopwatch.Stop()

        KillAll()
        RecordTrialData(completedBy)

        Await Task.Delay(1000)

        currentTrial += 1
        StartTrial()

    End Sub

    Private Sub KillAll()
        For i = 0 To 7
            If leftAlive(i) Then KillStim(leftRects(i)) : leftAlive(i) = False
            If rightAlive(i) Then KillStim(rightRects(i)) : rightAlive(i) = False
        Next
    End Sub


    ' ============================================
    ' DATA RECORDING
    ' ============================================
    Private Sub RecordTrialData(trialCompletedBy As String)

        completedBy = trialCompletedBy

        ' Update control panel with final values
        lblBubbleTouches.Content = bubbleTouchCount
        lblOddityWins.Content = oddityWinCount
        lblOddityErrors.Content = oddityErrorCount
        lblCompletedBy.Content = completedBy
        lblTrialTime.Content = trialStopwatch.ElapsedMilliseconds

        ' Build touch log string (semicolon-separated entries)
        Dim touchLogStr As String = ""
        For Each entry In touchLog
            If touchLogStr <> "" Then touchLogStr &= ";"
            touchLogStr &= entry
        Next

        ' Compute layout info for ghost-touch analysis
        Dim targetCellPos As Integer = ComputeTargetCellPos()
        Dim targetSide As String = ComputeTargetSide()
        Dim leftPosStr As String = FormatPositionList(leftPositions)
        Dim rightPosStr As String = FormatPositionList(rightPositions)

        ' Compute FirstBubbleGhost:
        '   "NA" = trial has no bubble side or no oddity target (E, F, G, H, I, J)
        '   "1"  = first bubble touched was the ghost-target bubble
        '   "2"  = first bubble touched was a different bubble
        '   "3"  = no bubble was touched this trial
        Dim firstBubbleGhost As String = "NA"
        Select Case trialType
            Case "A", "B", "C", "D"
                If firstBubbleCellPos = -1 Then
                    firstBubbleGhost = "3"
                ElseIf firstBubbleCellPos = targetCellPos Then
                    firstBubbleGhost = "1"
                Else
                    firstBubbleGhost = "2"
                End If
        End Select

        ' ApeTouch convention: comma-space delimited single line per trial
        DataBox.Text = DataBox.Text &
            subjectName & " , " &
            speciesName & " , " &
            datestring & " , " &
            sessionNumber & " , " &
            locationName & " , " &
            (currentTrial + 1) & " , " &
            sessionTrials(currentTrial) & " , " &
            trialType & " , " &
            targetFace & " , " &
            sideCode & " , " &
            leftTask & " , " &
            rightTask & " , " &
            bubbleCount & " , " &
            oddityCount & " , " &
            targetCellPos & " , " &
            targetSide & " , " &
            leftPosStr & " , " &
            rightPosStr & " , " &
            If(isProbe, "Y", "N") & " , " &
            distractorType & " , " &
            completedBy & " , " &
            bubbleTouchCount & " , " &
            oddityWinCount & " , " &
            oddityErrorCount & " , " &
            oddTwoStimWin & " , " &
            firstBubbleGhost & " , " &
            latencyFirstTouch & " , " &
            latencyFirstTarget & " , " &
            trialStopwatch.ElapsedMilliseconds & " , " &
            touchLogStr & vbCrLf

        DataBox.ScrollToEnd()

        ' Update live metrics panel
        UpdateMetricsForTrial()

    End Sub

    Private Sub EndSession()
        Curtain.Visibility = Visibility.Visible
        lbl_StatusIndicator.Content = "COMPLETE"
        DataBox.ScrollToEnd()
    End Sub


    ' ============================================
    ' SAVE / CLEAR (ApeTouch pattern)
    ' ============================================
    Private Sub Save_Click(sender As Object, e As System.Windows.RoutedEventArgs)
        Dim SaveFileDialog1 As New Microsoft.Win32.SaveFileDialog
        SaveFileDialog1.Filter = "txt files (*.txt)|*.txt"
        SaveFileDialog1.FilterIndex = 2
        SaveFileDialog1.RestoreDirectory = True
        SaveFileDialog1.FileName = "SafetyPop_" & subjectName & "_S" & sessionNumber & "_" & datestring & "_" & mytimestring.Replace(":", "-")
        SaveFileDialog1.ShowDialog()
        If SaveFileDialog1.FileName <> "" Then
            System.IO.File.WriteAllText(SaveFileDialog1.FileName, DataBox.Text)
            dataStreamSaved = True
        End If
    End Sub

    Private Sub Clear_Click(sender As Object, e As System.Windows.RoutedEventArgs)
        DataBox.Text = ""
        dataStreamSaved = True
    End Sub


    ' ============================================
    ' PLAY/PAUSE
    ' Three states:
    '   1. Pre-session (sessionInitialized=False): first play press
    '      reads radio + dropdowns, builds sessionTrials, sets currentTrial,
    '      locks the controls, and starts the first trial.
    '   2. Running (curtain hidden): pause press pauses and shows curtain.
    '   3. Paused (curtain visible, sessionInitialized=True): play press
    '      restarts the current trial from the beginning (fresh positions,
    '      reset counters). Mid-trial progress is discarded.
    ' ============================================
    Private Sub pauseplay_Click(sender As Object, e As System.Windows.RoutedEventArgs) Handles pauseplay.Click

        If Not sessionInitialized Then
            ' First press: configure session and start
            InitializeSessionFromUI()
            Exit Sub
        End If

        If Curtain.Visibility = Visibility.Hidden Then
            ' Currently running -> pause
            Curtain.Visibility = Visibility.Visible
            trialActive = False
            PlayIcon.Visibility = Visibility.Visible
            PauseIcon.Visibility = Visibility.Hidden
            lbl_StatusIndicator.Content = "PAUSED"
        Else
            ' Currently paused -> resume by restarting current trial
            PlayIcon.Visibility = Visibility.Hidden
            PauseIcon.Visibility = Visibility.Visible
            lbl_StatusIndicator.Content = "RUNNING"
            Curtain.Visibility = Visibility.Hidden
            ' StartTrial fully resets rectangles, positions, counters, touchLog
            ' for the current trial -- equivalent to a fresh attempt at the
            ' same trial number.
            StartTrial()
        End If

    End Sub


    ' ============================================
    ' SESSION INITIALIZATION (first play press)
    ' Reads UI state to determine run mode and starting point, builds
    ' sessionTrials, locks the controls, and starts the first trial.
    ' ============================================
    Private Sub InitializeSessionFromUI()

        Dim selectedSessionNum As Integer = cmbSessionNumber.SelectedIndex + 1
        Dim selectedStartTrial As Integer = cmbStartTrial.SelectedIndex  ' 0-indexed

        If rbModeFixed.IsChecked Then
            ' Mode 2: pick the pre-generated sequence for the selected session
            sessionTrials = fixedSequences(selectedSessionNum - 1)
            currentTrial = selectedStartTrial
        Else
            ' Mode 1: fresh random shuffle, always start at trial 1
            sessionTrials = GenerateRandomSequence()
            currentTrial = 0
        End If

        sessionNumber = selectedSessionNum.ToString()
        lbl_Session.Content = sessionNumber

        ' Commit the participant selection from the dropdown
        If Not String.IsNullOrEmpty(subject.Text) Then
            subjectName = subject.Text
            lbl_Subject.Content = subjectName
            lbldbsubject.Content = subjectName
        End If

        sessionInitialized = True
        sessionStartTime = DateTime.Now
        dataStreamSaved = True
        metricsSaved = True
        ResetMetricsAggregators()

        ' Lock the configuration controls now that the session is committed
        rbModeFixed.IsEnabled = False
        rbModeRandom.IsEnabled = False
        cmbSessionNumber.IsEnabled = False
        cmbStartTrial.IsEnabled = False
        subject.IsEnabled = False
        lblRunModeHint.Content = "(session locked in)"

        ' Switch to running state
        PlayIcon.Visibility = Visibility.Hidden
        PauseIcon.Visibility = Visibility.Visible
        lbl_StatusIndicator.Content = "RUNNING"
        Curtain.Visibility = Visibility.Hidden

        StartTrial()

    End Sub


    ' ============================================
    ' RUN MODE TOGGLE — enable/disable dropdowns
    ' Random mode disables the starting-trial dropdown since a fresh random
    ' shuffle has no meaningful "resume from trial N" semantics.
    ' ============================================
    Private Sub RunMode_Changed(sender As Object, e As System.Windows.RoutedEventArgs)
        UpdateModeDropdownStates()
    End Sub

    Private Sub UpdateModeDropdownStates()
        If rbModeRandom Is Nothing OrElse cmbStartTrial Is Nothing Then Exit Sub
        If rbModeRandom.IsChecked Then
            cmbStartTrial.IsEnabled = False
        Else
            cmbStartTrial.IsEnabled = True
        End If
    End Sub


    ' ============================================
    ' SEQUENCE GENERATION
    ' GenerateSeededSequence builds a deterministic shuffle of the canonical
    ' 60 codes from a fixed seed -- used for the 20 fixed sequences in Mode 2.
    ' GenerateRandomSequence uses the shared Rng for Mode 1.
    ' ============================================
    Private Function GenerateSeededSequence(seed As Integer) As String()
        Dim seededRng As New Random(seed)
        Dim shuffled As New List(Of String)(canonical60Codes)
        For i As Integer = shuffled.Count - 1 To 1 Step -1
            Dim j As Integer = seededRng.Next(0, i + 1)
            Dim tmp As String = shuffled(i)
            shuffled(i) = shuffled(j)
            shuffled(j) = tmp
        Next
        Return shuffled.ToArray()
    End Function

    Private Function GenerateRandomSequence() As String()
        Dim shuffled As New List(Of String)(canonical60Codes)
        ShuffleList(shuffled)
        Return shuffled.ToArray()
    End Function


    ' ============================================
    ' HOME (ApeTouch: navigate back to MenuScreen)
    ' If either the data stream or the metrics have unsaved changes,
    ' prompt the operator to confirm before exiting. No prompt if
    ' nothing has been recorded yet, or if both streams are saved.
    ' ============================================
    Private Sub HomeKey_Click(sender As Object, e As System.Windows.RoutedEventArgs) Handles HomeKey.Click

        ' Anything to lose?
        Dim hasData As Boolean = trialTimes.Count > 0
        Dim anyUnsaved As Boolean = (Not dataStreamSaved) OrElse (Not metricsSaved)

        If hasData AndAlso anyUnsaved Then
            Dim msg As String = "Unsaved data:" & vbCrLf & vbCrLf
            If Not dataStreamSaved Then msg &= "  • Trial-by-trial data stream" & vbCrLf
            If Not metricsSaved Then msg &= "  • Session metrics summary" & vbCrLf
            msg &= vbCrLf & "Proceed without saving?"

            Dim result As MessageBoxResult = System.Windows.MessageBox.Show(
                msg, "Exit without saving?",
                MessageBoxButton.YesNo, MessageBoxImage.Warning,
                MessageBoxResult.No)

            If result <> MessageBoxResult.Yes Then Exit Sub
        End If

        gohome()
    End Sub

    Private Sub gohome()
        trialActive = False
        JustFinished = True
        Me.NavigationService.Navigate(New Uri("MenuScreen.xaml", UriKind.Relative))
    End Sub


    ' ============================================
    ' ANIMATION: KILL (pop then shrink to 0)
    ' ============================================
    Private Sub KillStim(rect As Rectangle)

        ' Clear any existing animations first
        rect.BeginAnimation(Rectangle.WidthProperty, Nothing)
        rect.BeginAnimation(Rectangle.HeightProperty, Nothing)
        rect.BeginAnimation(Rectangle.OpacityProperty, Nothing)

        rect.Width = 140
        rect.Height = 140

        ' Expand briefly then shrink to 0
        Dim animW As New DoubleAnimationUsingKeyFrames()
        animW.KeyFrames.Add(New EasingDoubleKeyFrame(150, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(80))))
        animW.KeyFrames.Add(New EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(330))))
        animW.FillBehavior = FillBehavior.HoldEnd

        Dim animH As New DoubleAnimationUsingKeyFrames()
        animH.KeyFrames.Add(New EasingDoubleKeyFrame(150, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(80))))
        animH.KeyFrames.Add(New EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(330))))
        animH.FillBehavior = FillBehavior.HoldEnd

        Dim animO As New DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(330))
        animO.FillBehavior = FillBehavior.HoldEnd

        rect.BeginAnimation(Rectangle.WidthProperty, animW)
        rect.BeginAnimation(Rectangle.HeightProperty, animH)
        rect.BeginAnimation(Rectangle.OpacityProperty, animO)

        rect.IsEnabled = False

    End Sub


    ' ============================================
    ' ANIMATION: REVIVE (grow from 0 to 140)
    ' ============================================
    Private Sub ReviveStim(rect As Rectangle)

        rect.BeginAnimation(Rectangle.WidthProperty, Nothing)
        rect.BeginAnimation(Rectangle.HeightProperty, Nothing)
        rect.BeginAnimation(Rectangle.OpacityProperty, Nothing)

        rect.Width = 0
        rect.Height = 0
        rect.Opacity = 1
        rect.Visibility = Visibility.Visible

        Dim ease As New QuadraticEase() With {.EasingMode = EasingMode.EaseOut}

        Dim animW As New DoubleAnimation(0, 140, TimeSpan.FromMilliseconds(200))
        animW.EasingFunction = ease
        animW.FillBehavior = FillBehavior.HoldEnd

        Dim animH As New DoubleAnimation(0, 140, TimeSpan.FromMilliseconds(200))
        animH.EasingFunction = ease
        animH.FillBehavior = FillBehavior.HoldEnd

        rect.BeginAnimation(Rectangle.WidthProperty, animW)
        rect.BeginAnimation(Rectangle.HeightProperty, animH)

    End Sub


    ' ============================================
    ' ANIMATION: JIGGLE (MC1-style dual elastic ease)
    ' Two overlapping animations per axis:
    '   1) Shrink: 170->140, 1s, ElasticEase osc=4 spring=2
    '   2) Grow:   140->170, 1.5s, ElasticEase osc=10 spring=1
    ' FillBehavior.Stop so stim returns to 140 after wobble
    ' ============================================
    Private Sub JiggleStim(rect As Rectangle)

        rect.BeginAnimation(Rectangle.WidthProperty, Nothing)
        rect.BeginAnimation(Rectangle.HeightProperty, Nothing)

        ' Base stays 140 so FillBehavior.Stop returns to 140
        rect.Width = 140
        rect.Height = 140

        Dim wobbleEase As New ElasticEase() With {
            .Oscillations = 8,
            .Springiness = 2,
            .EasingMode = EasingMode.EaseOut
        }

        ' Animate from 110 back to 140 with elastic overshoot
        ' Snaps small then wobbles back; peaks ~155px (within 160px cell)
        Dim animW As New DoubleAnimation(110, 140, TimeSpan.FromSeconds(1.5))
        animW.EasingFunction = wobbleEase
        animW.FillBehavior = FillBehavior.Stop

        Dim animH As New DoubleAnimation(110, 140, TimeSpan.FromSeconds(1.5))
        animH.EasingFunction = wobbleEase
        animH.FillBehavior = FillBehavior.Stop

        rect.BeginAnimation(Rectangle.WidthProperty, animW)
        rect.BeginAnimation(Rectangle.HeightProperty, animH)

    End Sub


    ' ============================================
    ' ANIMATION: RESET (clear all, restore defaults)
    ' ============================================
    Private Sub ResetStim(rect As Rectangle)

        rect.BeginAnimation(Rectangle.WidthProperty, Nothing)
        rect.BeginAnimation(Rectangle.HeightProperty, Nothing)
        rect.BeginAnimation(Rectangle.OpacityProperty, Nothing)

        rect.Width = 140
        rect.Height = 140
        rect.Opacity = 1
        rect.Visibility = Visibility.Hidden
        rect.IsEnabled = False
        rect.Tag = ""
        rect.Fill = System.Windows.Media.Brushes.Transparent

    End Sub


    ' ============================================
    ' FISHER-YATES SHUFFLE
    ' ============================================
    Private Sub ShuffleList(Of T)(list As List(Of T))
        For i As Integer = list.Count - 1 To 1 Step -1
            Dim j As Integer = Rng.Next(0, i + 1)
            Dim temp As T = list(i)
            list(i) = list(j)
            list(j) = temp
        Next
    End Sub


End Class