using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WallSetupManager : MonoBehaviour
{
    public GameObject visual;
    public Transform pivot;
    public Transform creationHand;
    public GameObject[] objectToSpawnAfter;
    private Vector3 startPosition;
    private bool isUpdatingShape;

    public float defaultWidth = 0.3f;
    public float defaultHeight = 0.01f;

    // Start is called before the first frame update
    void Start()
    {
        visual.SetActive(false);
        foreach (var item in objectToSpawnAfter)
        {
            item.SetActive(false);
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (OVRInput.GetDown(OVRInput.Button.SecondaryIndexTrigger))
        {
            visual.SetActive(true);
            startPosition = creationHand.position;
            isUpdatingShape = true;
        }
        else if (OVRInput.GetUp(OVRInput.Button.SecondaryIndexTrigger))
        {
            isUpdatingShape = false;
            foreach (var item in objectToSpawnAfter)
            {
                item.SetActive(true);
            }

            // Disable the WallSetupManager script after creating the wall
            this.enabled = false;
        }

        if (isUpdatingShape)
        {
            UpdateShape();
        }
    }

    public void UpdateShape()
    {
        //Scaling the plane 
        float distanceY = Mathf.Abs(startPosition.y - creationHand.position.y);
        float distanceX = Mathf.Abs(startPosition.x - creationHand.position.x);
        visual.transform.localScale = new Vector3(distanceX, distanceY, defaultHeight);

        //Rotation
        pivot.right = Vector3.ProjectOnPlane(creationHand.position - startPosition, Vector3.up);

        //Position
        pivot.position = startPosition + pivot.rotation * new Vector3(visual.transform.localScale.x / 2, -visual.transform.localScale.y / 2, 0);
    }
}
