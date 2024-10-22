from django import forms

class IndicatorForm(forms.Form):
    symbol = forms.CharField(label='Stock Symbol', max_length=10, initial='IBM')
    function = forms.ChoiceField(
        choices=[
            ('HT_PHASOR', 'HT_PHASOR'),
            # Add other indicators if needed
        ],
        initial='HT_PHASOR'
    )
    interval = forms.ChoiceField(
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        initial='weekly'
    )
    series_type = forms.ChoiceField(
        choices=[
            ('close', 'Close'),
            ('open', 'Open'),
            ('high', 'High'),
            ('low', 'Low'),
        ],
        initial='close'
    )
