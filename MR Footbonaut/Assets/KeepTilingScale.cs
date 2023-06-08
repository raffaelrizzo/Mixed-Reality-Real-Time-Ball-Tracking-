using UnityEngine;

public class KeepTilingScale : MonoBehaviour
{
    public float xScaleMult = 1;
    public float yScaleMult = 1;
    private Material material;

    private Material Material
    {
        get
        {
            if (material == null)
            {
                MeshRenderer render = GetComponent<MeshRenderer>();
#if UNITY_EDITOR
                material = render.sharedMaterial;
#else
                material = render.material;
#endif
            }
            return material;
        }
    }
    // Update is called once per frame
    void Update()
    {
        //set the material scale based on the size of the object
        Material.mainTextureScale = new Vector2(xScaleMult * transform.lossyScale.magnitude / transform.localScale.z, yScaleMult * transform.lossyScale.magnitude / transform.localScale.x );
    }
}