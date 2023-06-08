using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR;

public class OVRTransformController : MonoBehaviour
{
    public Transform playerTransform;
    private Vector3 initialPosition;
    private Quaternion initialRotation;

    void Start()
    {
        initialPosition = transform.position;
        initialRotation = transform.rotation;
    }

    void Update()
{
    if (OVRInput.GetDown(OVRInput.Button.PrimaryIndexTrigger))
    {
        Debug.Log("PrimaryIndexTrigger pressed");
        ResetCameraPosition();
        // this.transform.position = playerTransform.position;
        // this.transform.rotation = playerTransform.rotation;
    }
}

private void ResetCameraPosition()
{
    // Calculate difference between player and initial position
    Vector3 positionDifference = playerTransform.position - initialPosition;
    Debug.Log("Position Difference: " + positionDifference);

    // Ignore y coordinate, we only care about x and z for horizontal movement
    positionDifference.y = 0;

    // Reset position and rotation
    transform.position = initialPosition + positionDifference;
    transform.rotation = initialRotation;
}

}