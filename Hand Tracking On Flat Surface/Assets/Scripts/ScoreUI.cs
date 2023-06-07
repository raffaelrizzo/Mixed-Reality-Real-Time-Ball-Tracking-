using UnityEngine;
using TMPro;  // Use UnityEngine.UI if you're using Text instead of TextMeshPro

public class ScoreUI : MonoBehaviour
{
    public ScoreManager scoreManager;
    private TextMeshProUGUI textMeshPro;  // Use Text instead if you're using Text

    private void Start()
    {
        // Get the TextMeshPro component
        textMeshPro = GetComponent<TextMeshProUGUI>();  // Use GetComponent<Text>() if you're using Text
    }

    private void Update()
    {
        // Update the text to display the current score
        textMeshPro.text = "Score: " + scoreManager.score;
    }
}
