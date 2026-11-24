' ================================================================
' SafetyPopMenu — secondary menu for the SafetyPop family.
'
' Reached from the SafetyPop icon on MenuScreen (SPpauseplay_Click), mirroring
' the DotMenu / MTSMenu pattern. Offers the two SafetyPop variants:
'   SP1But -> SafetyPop.xaml   (v1, original oddity task with emotional faces)
'   SP2But -> SafetyPop2.xaml  (v2, simplified discrimination task)
' ================================================================
Class SafetyPopMenu

    Private Sub SP1But_Click(sender As Object, e As RoutedEventArgs) Handles SP1But.Click
        SessionMode = "Open"
        Me.NavigationService.Navigate(New Uri("SafetyPop.xaml", UriKind.Relative))
    End Sub

    Private Sub SP2But_Click(sender As Object, e As RoutedEventArgs) Handles SP2But.Click
        SessionMode = "Open"
        Me.NavigationService.Navigate(New Uri("SafetyPop2.xaml", UriKind.Relative))
    End Sub

End Class
