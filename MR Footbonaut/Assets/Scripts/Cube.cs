using UnityEngine;

public class Cube : MonoBehaviour
{
    public Material lightUpMaterial;
    public Material defaultMaterial;

    private Renderer cubeRenderer;
    private bool isLit;

    private void Start()
    {
        cubeRenderer = GetComponent<Renderer>();
        cubeRenderer.material = defaultMaterial;
        isLit = false;
    }

    public void LightUp()
    {
        cubeRenderer.material = lightUpMaterial;
        isLit = true;
    }

    public void TurnOffLight()
    {
        cubeRenderer.material = defaultMaterial;
        isLit = false;
    }

    public bool IsLit()
    {
        return isLit;
    }
}
